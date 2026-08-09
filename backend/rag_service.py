from pathlib import Path
import json
import re

import chromadb
from openai import OpenAI
from sentence_transformers import SentenceTransformer


# ============================================================
# CONFIGURATION
# ============================================================

BASE_DIR = Path(__file__).parent

CHROMA_PATH = BASE_DIR / "chroma_db"

KNOWLEDGE_BASE = BASE_DIR / "student_schemes.md"

SCHEMES_JSON = BASE_DIR / "schemes.json"

EMBEDDING_MODEL = "all-MiniLM-L6-v2"

LLM_MODEL = "llama3.2:1b"

COLLECTION_NAME = "government_schemes"

TOP_K = 4

MIN_RELEVANCE = 0.20


# ============================================================
# EMBEDDING MODEL
# ============================================================

print("Loading embedding model...")

embedding_model = SentenceTransformer(
    EMBEDDING_MODEL
)


# ============================================================
# LOCAL OLLAMA
# ============================================================

llm = OpenAI(
    base_url="http://localhost:11434/v1",
    api_key="ollama",
)


# ============================================================
# CHROMADB
# ============================================================

chroma_client = chromadb.PersistentClient(
    path=str(CHROMA_PATH)
)

collection = chroma_client.get_or_create_collection(
    name=COLLECTION_NAME
)


# ============================================================
# LOAD STRUCTURED SCHEMES
# ============================================================

def load_schemes():

    if not SCHEMES_JSON.exists():
        return []

    try:

        with open(
            SCHEMES_JSON,
            "r",
            encoding="utf-8"
        ) as file:

            data = json.load(file)

        return data.get(
            "schemes",
            []
        )

    except Exception as error:

        print(
            f"Warning: Could not load schemes.json: {error}"
        )

        return []


SCHEMES = load_schemes()


# ============================================================
# TEXT NORMALIZATION
# ============================================================

def normalize_text(value):

    if value is None:
        return ""

    return str(value).strip().lower()


# ============================================================
# SIMPLE KEYWORD RELEVANCE
# ============================================================

def keyword_score(
    question: str,
    document: str,
) -> float:

    question_words = set(
        re.findall(
            r"[a-zA-Z0-9]+",
            normalize_text(question)
        )
    )

    document_words = set(
        re.findall(
            r"[a-zA-Z0-9]+",
            normalize_text(document)
        )
    )

    if not question_words:
        return 0.0

    overlap = (
        question_words
        & document_words
    )

    return len(overlap) / len(question_words)


# ============================================================
# RAG RETRIEVAL
# ============================================================

def retrieve_context(
    question: str,
    top_k: int = TOP_K,
):

    query_embedding = embedding_model.encode(
        [question]
    ).tolist()

    results = collection.query(
        query_embeddings=query_embedding,
        n_results=top_k,
        include=[
            "documents",
            "metadatas",
            "distances",
        ],
    )

    documents = (
        results.get(
            "documents",
            [[]]
        )[0]
    )

    metadatas = (
        results.get(
            "metadatas",
            [[]]
        )[0]
    )

    distances = (
        results.get(
            "distances",
            [[]]
        )[0]
    )

    retrieved = []

    for index, document in enumerate(documents):

        distance = (
            distances[index]
            if index < len(distances)
            else 1.0
        )

        metadata = (
            metadatas[index]
            if index < len(metadatas)
            else {}
        )

        # Chroma cosine distance is lower when
        # documents are more relevant.
        semantic_score = max(
            0.0,
            1.0 - float(distance)
        )

        keyword = keyword_score(
            question,
            document
        )

        combined_score = (
            semantic_score * 0.75
            + keyword * 0.25
        )

        retrieved.append(
            {
                "document": document,
                "metadata": metadata or {},
                "score": combined_score,
            }
        )

    retrieved.sort(
        key=lambda item: item["score"],
        reverse=True,
    )

    return retrieved


# ============================================================
# SOURCE INFORMATION
# ============================================================

OFFICIAL_SOURCE = {
    "title": (
        "Government of India, Ministry of Education — "
        "PM-USP CSSS 2025-26 FAQ"
    ),
    "url": (
        "https://www.education.gov.in/sites/"
        "upload_files/mhrd/files/upload_document/"
        "FAQs_PM_USP2526.pdf"
    ),
}


# ============================================================
# ASK CIVICAI
# ============================================================

def ask_civic_ai(
    question: str,
) -> dict:

    question = question.strip()

    if not question:

        return {
            "answer": "Please enter a question.",
            "sources": [],
            "matched_schemes": [],
        }


    # --------------------------------------------------------
    # RETRIEVE
    # --------------------------------------------------------

    retrieved = retrieve_context(
        question
    )

    relevant = [
        item
        for item in retrieved
        if item["score"] >= MIN_RELEVANCE
    ]


    # --------------------------------------------------------
    # NO RELEVANT INFORMATION
    # --------------------------------------------------------

    if not relevant:

        return {
            "answer": (
                "I couldn't find enough verified information "
                "in the CivicAI knowledge base to answer "
                "that question safely."
            ),
            "sources": [],
            "matched_schemes": [],
        }


    # --------------------------------------------------------
    # BUILD CONTEXT
    # --------------------------------------------------------

    context_parts = []

    for item in relevant:

        context_parts.append(
            item["document"]
        )

    context = "\n\n---\n\n".join(
        context_parts
    )


    # --------------------------------------------------------
    # AI PROMPT
    # --------------------------------------------------------

    system_prompt = """
You are CivicAI, an AI assistant that explains
Indian government schemes and services.

You MUST follow these rules:

1. Use ONLY the supplied CONTEXT.
2. Never invent government schemes.
3. Never invent eligibility criteria.
4. Never invent benefit amounts.
5. Never invent application deadlines.
6. Never invent documents required.
7. Never claim that a user is officially eligible.
8. If information is missing, explicitly say that it
   is not available in the CivicAI knowledge base.
9. Clearly distinguish between eligibility requirements
   and final government selection.
10. Keep answers simple and useful.
11. Use numbered lists or bullet points where appropriate.
12. Mention important exclusions when they are present.
13. Do not say something is "officially confirmed" unless
    that exact information is present in CONTEXT.
14. When a source is available, tell the user to verify
    the latest details on the official government source.
"""

    user_prompt = f"""
CONTEXT:

{context}

USER QUESTION:

{question}

Answer the user's question using only the context above.
"""


    # --------------------------------------------------------
    # GENERATE
    # --------------------------------------------------------

    try:

        response = llm.chat.completions.create(

            model=LLM_MODEL,

            messages=[
                {
                    "role": "system",
                    "content": system_prompt,
                },
                {
                    "role": "user",
                    "content": user_prompt,
                },
            ],

            temperature=0.1,

        )

        answer = (
            response
            .choices[0]
            .message
            .content
            .strip()
        )

    except Exception as error:

        print(
            f"Ollama error: {error}"
        )

        return {
            "answer": (
                "CivicAI could not connect to the local "
                "AI model. Please make sure Ollama is running."
            ),
            "sources": [],
            "matched_schemes": [],
        }


    # --------------------------------------------------------
    # SOURCES
    # --------------------------------------------------------

    sources = [
        OFFICIAL_SOURCE
    ]


    # --------------------------------------------------------
    # MATCHED SCHEMES
    # --------------------------------------------------------

    matched_schemes = []

    for scheme in SCHEMES:

        scheme_name = normalize_text(
            scheme.get("name", "")
        )

        question_lower = normalize_text(
            question
        )

        if (
            scheme_name
            and (
                scheme_name in question_lower
                or any(
                    word in question_lower
                    for word in scheme_name.split()
                    if len(word) > 4
                )
            )
        ):

            matched_schemes.append(
                scheme
            )


    return {
        "answer": answer,
        "sources": sources,
        "matched_schemes": matched_schemes,
    }


# ============================================================
# SCHEME FINDER
# ============================================================

def find_matching_schemes(
    profile: dict,
):

    if not SCHEMES:
        return []


    results = []

    for scheme in SCHEMES:

        score = 0
        reasons = []
        warnings = []

        eligibility = scheme.get(
            "eligibility",
            {}
        )


        # ----------------------------------------------------
        # EDUCATION
        # ----------------------------------------------------

        user_education = normalize_text(
            profile.get("education")
        )

        education_levels = [
            normalize_text(level)
            for level in eligibility.get(
                "education",
                []
            )
        ]

        if user_education:

            if (
                not education_levels
                or user_education in education_levels
            ):

                score += 20

                reasons.append(
                    "Your education level matches "
                    "the available scheme information."
                )


        # ----------------------------------------------------
        # INCOME
        # ----------------------------------------------------

        user_income = profile.get(
            "annual_income"
        )

        max_income = eligibility.get(
            "max_income"
        )

        if (
            user_income is not None
            and max_income is not None
        ):

            if user_income <= max_income:

                score += 30

                reasons.append(
                    "Your reported annual income "
                    "is within the stated income limit."
                )

            else:

                warnings.append(
                    "Your reported annual income is "
                    "above the stated income limit."
                )


        # ----------------------------------------------------
        # AGE
        # ----------------------------------------------------

        user_age = profile.get(
            "age"
        )

        min_age = eligibility.get(
            "min_age"
        )

        max_age = eligibility.get(
            "max_age"
        )

        if user_age is not None:

            age_ok = True

            if (
                min_age is not None
                and user_age < min_age
            ):
                age_ok = False

            if (
                max_age is not None
                and user_age > max_age
            ):
                age_ok = False

            if age_ok:

                score += 15

                reasons.append(
                    "Your age is compatible with "
                    "the available scheme criteria."
                )

            else:

                warnings.append(
                    "Your age may not meet the stated "
                    "scheme criteria."
                )


        # ----------------------------------------------------
        # OCCUPATION
        # ----------------------------------------------------

        user_occupation = normalize_text(
            profile.get("occupation")
        )

        occupations = [
            normalize_text(value)
            for value in eligibility.get(
                "occupations",
                []
            )
        ]

        if user_occupation and occupations:

            if user_occupation in occupations:

                score += 15

                reasons.append(
                    "Your occupation matches the "
                    "scheme category."
                )


        # ----------------------------------------------------
        # CATEGORY
        # ----------------------------------------------------

        user_category = normalize_text(
            profile.get("category")
        )

        scheme_category = normalize_text(
            scheme.get("category")
        )

        if user_category:

            if (
                user_category == scheme_category
                or user_category in scheme_category
                or scheme_category in user_category
            ):

                score += 20

                reasons.append(
                    "The scheme category matches "
                    "your selected interest."
                )


        # ----------------------------------------------------
        # STATE
        # ----------------------------------------------------

        user_state = normalize_text(
            profile.get("state")
        )

        scheme_states = [
            normalize_text(value)
            for value in scheme.get(
                "states",
                ["all"]
            )
        ]

        if user_state:

            if (
                "all" in scheme_states
                or user_state in scheme_states
            ):

                score += 10


        # ----------------------------------------------------
        # RESULT
        # ----------------------------------------------------

        if score > 0:

            match_percentage = min(
                score,
                100
            )

            results.append(
                {
                    "id": scheme.get("id"),
                    "name": scheme.get("name"),
                    "short_name": scheme.get(
                        "short_name"
                    ),
                    "category": scheme.get(
                        "category"
                    ),
                    "government": scheme.get(
                        "government"
                    ),
                    "objective": scheme.get(
                        "objective"
                    ),
                    "benefit": scheme.get(
                        "benefit"
                    ),
                    "application": scheme.get(
                        "application"
                    ),
                    "match_percentage": match_percentage,
                    "reasons": reasons,
                    "warnings": warnings,
                    "source": scheme.get(
                        "source",
                        OFFICIAL_SOURCE
                    ),
                    "disclaimer": (
                        "This is an informational match "
                        "based on the CivicAI knowledge base. "
                        "It does not constitute official "
                        "eligibility or selection."
                    ),
                }
            )


    results.sort(
        key=lambda item: item[
            "match_percentage"
        ],
        reverse=True,
    )

    return results


# ============================================================
# GET ALL SCHEMES
# ============================================================

def get_all_schemes():

    return SCHEMES


# ============================================================
# LOCAL TEST
# ============================================================

if __name__ == "__main__":

    print()
    print("=" * 65)
    print("CIVICAI RAG SERVICE")
    print("=" * 65)

    result = ask_civic_ai(
        "What are the eligibility requirements "
        "for the scholarship?"
    )

    print()
    print("AI ANSWER:")
    print("-" * 65)
    print(result["answer"])

    print()
    print("SOURCES:")
    print("-" * 65)

    for source in result["sources"]:

        print(
            f"- {source['title']}"
        )
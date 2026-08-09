from pathlib import Path

import chromadb
from openai import OpenAI
from sentence_transformers import SentenceTransformer


# ============================================================
# PATHS
# ============================================================

BASE_DIR = Path(__file__).parent.parent

DATA_FILE = (
    BASE_DIR
    / "data"
    / "schemes"
    / "student_schemes.md"
)

CHROMA_PATH = (
    Path(__file__).parent
    / "chroma_db"
)


# ============================================================
# 1. READ KNOWLEDGE BASE
# ============================================================

text = DATA_FILE.read_text(encoding="utf-8").strip()

print(f"Loaded knowledge base: {DATA_FILE.name}")


# For our first prototype, keep the entire scheme
# as one coherent chunk.
chunks = [text]

print(f"Created {len(chunks)} knowledge chunk.")


# ============================================================
# 2. LOAD EMBEDDING MODEL
# ============================================================

embedding_model = SentenceTransformer(
    "all-MiniLM-L6-v2"
)


# ============================================================
# 3. CREATE LOCAL CHROMADB
# ============================================================

chroma_client = chromadb.PersistentClient(
    path=str(CHROMA_PATH)
)


# ============================================================
# 4. RESET OUR COLLECTION
# ============================================================

try:
    chroma_client.delete_collection(
        name="government_schemes"
    )
    print("Deleted old government_schemes collection.")
except Exception:
    pass


collection = chroma_client.create_collection(
    name="government_schemes"
)


# ============================================================
# 5. CREATE EMBEDDING
# ============================================================

embeddings = embedding_model.encode(
    chunks
).tolist()


# ============================================================
# 6. STORE KNOWLEDGE IN CHROMADB
# ============================================================

collection.add(
    ids=["scheme_001"],
    documents=chunks,
    embeddings=embeddings,
)

print("Stored knowledge in ChromaDB.")


# ============================================================
# 7. CONNECT TO LOCAL OLLAMA
# ============================================================

llm = OpenAI(
    base_url="http://localhost:11434/v1",
    api_key="ollama"
)


# ============================================================
# 8. USER QUESTION
# ============================================================

query = (
    "List all the eligibility requirements for "
    "the scholarship as bullet points."
)


# ============================================================
# 9. EMBED THE QUESTION
# ============================================================

query_embedding = embedding_model.encode(
    [query]
).tolist()


# ============================================================
# 10. RETRIEVE RELEVANT KNOWLEDGE
# ============================================================

results = collection.query(
    query_embeddings=query_embedding,
    n_results=1,
)


retrieved_documents = results["documents"][0]

context = "\n\n".join(
    retrieved_documents
)


# ============================================================
# 11. SHOW RETRIEVED CONTEXT
# ============================================================

print("\nRetrieved context:")
print("=" * 60)
print(context)
print("=" * 60)


# ============================================================
# 12. ASK OLLAMA USING ONLY RETRIEVED CONTEXT
# ============================================================

response = llm.chat.completions.create(
    model="llama3.2:1b",
    messages=[
        {
            "role": "system",
            "content": (
    "You are CivicAI, a government services assistant.\n\n"
    "Your job is to answer the user's question using "
    "the provided context.\n\n"

    "IMPORTANT RULES:\n"
    "1. Use the context as your source of truth.\n"
    "2. Extract and clearly present information that "
    "directly answers the question.\n"
    "3. Do not invent facts that are not in the context.\n"
    "4. Do not say the information is insufficient if "
    "the context directly contains the answer.\n"
    "5. If only some information is available, provide "
    "what is available and clearly state what is missing.\n"
    "6. Do not add unrelated information.\n"
)
        },
        {
            "role": "user",
            "content": (
                f"CONTEXT:\n\n"
                f"{context}\n\n\n"
                f"QUESTION:\n\n"
                f"{query}"
            ),
        },
    ],
)


# ============================================================
# 13. DISPLAY FINAL ANSWER
# ============================================================

answer = response.choices[0].message.content

print("\nAI Answer:")
print("=" * 60)
print(answer)
print("=" * 60)
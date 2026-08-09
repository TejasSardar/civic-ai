from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from rag_service import (
    ask_civic_ai,
    find_matching_schemes,
    get_all_schemes,
)


# ============================================================
# CIVICAI API
# ============================================================

app = FastAPI(
    title="CivicAI",
    description=(
        "AI-powered government services assistant "
        "using local RAG and Ollama."
    ),
    version="2.0.0",
)


# ============================================================
# CORS
# ============================================================

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================================
# REQUEST MODELS
# ============================================================

class ChatRequest(BaseModel):
    message: str


class SchemeFinderRequest(BaseModel):
    age: int | None = None
    education: str | None = None
    state: str | None = None
    occupation: str | None = None
    annual_income: float | None = None
    category: str | None = None


# ============================================================
# HEALTH CHECK
# ============================================================

@app.get("/")
def root():
    return {
        "name": "CivicAI",
        "message": "AI-powered government services assistant",
        "status": "healthy",
        "version": "2.0.0",
        "ai": "Ollama",
        "rag": "ChromaDB",
    }


@app.get("/health")
def health():
    return {
        "status": "healthy",
        "service": "CivicAI",
    }


# ============================================================
# CHAT
# ============================================================

@app.post("/chat")
def chat(request: ChatRequest):

    result = ask_civic_ai(
        request.message
    )

    return {
        "answer": result["answer"],
        "sources": result["sources"],
        "matched_schemes": result.get(
            "matched_schemes",
            []
        ),
    }


# ============================================================
# SCHEME FINDER
# ============================================================

@app.post("/find-schemes")
def find_schemes(request: SchemeFinderRequest):

    profile = {
        "age": request.age,
        "education": request.education,
        "state": request.state,
        "occupation": request.occupation,
        "annual_income": request.annual_income,
        "category": request.category,
    }

    results = find_matching_schemes(
        profile
    )

    return {
        "results": results,
        "count": len(results),
    }


# ============================================================
# ALL AVAILABLE SCHEMES
# ============================================================

@app.get("/schemes")
def schemes():

    return {
        "schemes": get_all_schemes()
    }
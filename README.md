# 🇮🇳 CivicAI

### AI-Powered Government Services Assistant

CivicAI is an AI-powered government information assistant designed to make Indian government scheme information easier to understand.

It combines **Retrieval-Augmented Generation (RAG)**, **semantic search**, **ChromaDB**, **Sentence Transformers**, **FastAPI**, and a **local Ollama LLM** to provide grounded answers from a curated government-scheme knowledge base.

> ⚠️ CivicAI provides informational guidance and does not determine official government eligibility, approval, selection, or entitlement. Important information should always be verified with the relevant government authority.

---

## ✨ Features

- 🤖 AI-powered government information assistant
- 🔎 Semantic search over government-scheme information
- 🧠 Retrieval-Augmented Generation (RAG)
- 📚 Curated government-scheme knowledge base
- 🗄️ ChromaDB vector database
- 🔤 Sentence Transformers embeddings
- 🦙 Local LLM inference using Ollama
- ⚡ FastAPI backend
- 💬 Interactive web interface
- 🔗 Official government source references
- 🛡️ Grounded responses designed to reduce hallucinations
- 💰 No paid LLM API required for the core AI pipeline

---

## 🎯 Why CivicAI?

Government schemes often contain eligibility requirements, exclusions, application procedures, and other information that can be difficult to understand.

CivicAI aims to make this information easier to access by allowing users to ask questions in natural language.

Instead of simply sending a question to an LLM, CivicAI first retrieves relevant information from its knowledge base and then uses that information to generate the response.

This makes the system a practical example of a **grounded RAG application** rather than a basic chatbot.

---

## 🧠 How CivicAI Works

CivicAI follows a Retrieval-Augmented Generation pipeline.

```text
                         User Question
                              │
                              ▼
                    ┌──────────────────┐
                    │    Frontend      │
                    │   HTML/CSS/JS    │
                    └────────┬─────────┘
                             │
                             ▼
                    ┌──────────────────┐
                    │     FastAPI      │
                    │     Backend      │
                    └────────┬─────────┘
                             │
                             ▼
                    ┌──────────────────┐
                    │ Sentence         │
                    │ Transformers     │
                    │   Embeddings     │
                    └────────┬─────────┘
                             │
                             ▼
                    ┌──────────────────┐
                    │    ChromaDB      │
                    │  Vector Search   │
                    └────────┬─────────┘
                             │
                             ▼
                      Relevant Context
                             │
                             ▼
                    ┌──────────────────┐
                    │     Ollama       │
                    │   Llama 3.2:1b   │
                    └────────┬─────────┘
                             │
                             ▼
                       Grounded Answer
                             │
                             ▼
                    ┌──────────────────┐
                    │    Frontend      │
                    └──────────────────┘
🔍 RAG Pipeline
1. User asks a question

For example:

What are the eligibility requirements for the scholarship?

2. Question is converted into an embedding

CivicAI uses Sentence Transformers to convert the user's question into a numerical vector representation.

3. Semantic retrieval

The question embedding is searched against the CivicAI knowledge base using ChromaDB.

The system retrieves information that is semantically relevant to the user's question.

4. Retrieved context is provided to the LLM

The relevant information retrieved from the knowledge base is passed to the local LLM as context.

5. Grounded response generation

Ollama runs the local LLM and generates an answer based on the retrieved context.

CivicAI's system instructions explicitly discourage the model from:

inventing eligibility requirements
inventing benefit amounts
inventing deadlines
guessing missing information
claiming official eligibility or selection

If the available context is insufficient, the system is instructed to say so instead of making up information.

6. Source information is returned

The API returns the generated answer together with relevant official source information.

🛡️ Grounded AI

A major design goal of CivicAI is reducing unsupported AI-generated information.

The RAG service instructs the model to:

use retrieved context as the source of truth
avoid inventing facts
avoid guessing missing information
avoid creating eligibility requirements
avoid creating benefit amounts
avoid creating deadlines
avoid claiming that a user is officially eligible
clearly state when information is insufficient
mention important exclusions when they are present in the context

This helps CivicAI behave differently from a general-purpose chatbot that can freely generate information from its pretrained knowledge.

🛠️ Tech Stack
Technology	Purpose
Python	Core application
FastAPI	Backend REST API
Ollama	Local LLM inference
Llama 3.2:1b	Local language model
ChromaDB	Vector database and semantic retrieval
Sentence Transformers	Text embeddings
HTML	Frontend structure
CSS	Frontend styling
JavaScript	Frontend interaction
uv	Python dependency and environment management
📁 Project Structure
civic-ai/
│
├── backend/
│   ├── main.py
│   ├── rag.py
│   ├── rag_service.py
│   ├── schemes.json
│   ├── chroma_db/          # Generated locally; ignored by Git
│   └── .venv/              # Local virtual environment; ignored by Git
│
├── data/
│   └── schemes/
│       └── student_schemes.md
│
├── docs/
│
├── frontend/
│   ├── index.html
│   ├── script.js
│   └── style.css
│
├── .gitignore
├── README.md
└── LICENSE

The chroma_db/ and virtual-environment directories are local/generated resources and are excluded from Git using .gitignore.

🚀 Getting Started
Prerequisites

Make sure you have the following installed:

Python
uv
Ollama

CivicAI currently uses the local Ollama model:

llama3.2:1b

You can verify your installed Ollama models with:

ollama list

If the model is not available, install it with:

ollama pull llama3.2:1b
📦 Install Dependencies

Open a terminal in the project directory and move into the backend:

cd backend

Install the required packages:

uv pip install fastapi uvicorn openai python-dotenv chromadb sentence-transformers
🗄️ Build the Knowledge Base

CivicAI uses curated government-scheme information stored in:

data/schemes/student_schemes.md

The RAG preparation script processes the knowledge base and stores the information in ChromaDB.

From the backend directory, run:

uv run python rag.py

A successful run creates/stores the knowledge required for semantic retrieval.

🦙 Start Ollama

Make sure Ollama is running and the required model is available:

ollama run llama3.2:1b

CivicAI uses Ollama locally, so no paid LLM API key is required for the core application.

⚡ Start the Backend

From the backend directory:

uv run uvicorn main:app --reload

The FastAPI server will run at:

http://127.0.0.1:8000

FastAPI's interactive API documentation is available at:

http://127.0.0.1:8000/docs
🌐 Frontend

The frontend is located in:

frontend/

It contains:

index.html
script.js
style.css

The frontend communicates with the FastAPI backend to:

send the user's question
receive the AI-generated response
display the answer
display the available source information
🔌 API
Health Check
GET /

Returns the health status of the CivicAI API.

Example response:

{
  "message": "CivicAI API is running",
  "status": "healthy"
}
Ask CivicAI
POST /chat

Send a question to CivicAI.

Request
{
  "message": "What are the eligibility requirements?"
}
Response
{
  "answer": "According to the available government information...",
  "sources": [
    {
      "title": "Government of India, Ministry of Education — PM-USP CSSS 2025-26 FAQ",
      "url": "https://www.education.gov.in/sites/upload_files/mhrd/files/upload_document/FAQs_PM_USP2526.pdf"
    }
  ]
}
💬 Example Questions

Users can ask CivicAI questions such as:

What are the eligibility requirements for the scholarship?

What is the annual family income limit?

Are diploma students eligible?

How can I apply?

What is the objective of the scheme?

Which government department manages the scheme?

The quality and scope of the response depend on the information available in the CivicAI knowledge base.

📚 Knowledge Base

CivicAI currently uses a curated government-scheme knowledge base.

The project includes information about:

Pradhan Mantri Uchchatar Shiksha Protsahan (PM-USP)

and

Central Sector Scheme of Scholarship for College and University Students (CSSS)

The knowledge base contains information such as:

Objective
Eligibility
Important exclusions
Application information
Government department
Official source information

The system is designed to use the knowledge base as its source of truth rather than relying on the LLM's general knowledge.

🏛️ Official Source

The current knowledge base references official documentation from:

Government of India — Ministry of Education

PM-USP Central Sector Scheme of Scholarship for College and University Students (CSSS), 2025-26 FAQ.

Official source:

https://www.education.gov.in/sites/upload_files/mhrd/files/upload_document/FAQs_PM_USP2526.pdf

📸 Screenshots
CivicAI Interface

![img.png](img.png)


Example AI Response

 ![img_1.png](img_1.png)
 
 
⚠️ Limitations

CivicAI is currently a prototype with a limited knowledge base.

Important limitations include:

The knowledge base currently covers a limited number of government schemes.
Information is only as current as the underlying knowledge base.
The AI response should not be treated as an official government decision.
Users should verify important requirements with the relevant government authority.
The system currently runs locally.
Retrieval quality depends on the quality and coverage of the knowledge base.
🚀 Future Improvements

Potential future improvements include:

🇮🇳 Add more Indian government schemes
🌐 Multilingual support for Indian languages
🔄 Automated government information updates
📄 Automatic ingestion of government PDFs
🎯 Personalized scheme discovery
🔎 Improved retrieval and ranking
📊 Better source attribution
☁️ Cloud deployment
🔐 User accounts and saved searches
📱 Further mobile optimization
🧪 Automated RAG evaluation
📈 Retrieval and response quality monitoring
🎯 Project Goal

The goal of CivicAI is to demonstrate how modern AI engineering techniques can be combined to build a practical application that solves a real-world information problem.

The project demonstrates:

RAG
 +
Embeddings
 +
Vector Search
 +
Local LLM
 +
FastAPI
 +
Web Interface

Rather than simply sending a prompt to an LLM and displaying its response, CivicAI introduces a retrieval layer that provides the model with relevant information from a controlled knowledge base.

🔒 Privacy

CivicAI is designed to run locally using Ollama for LLM inference.

The core AI pipeline does not require a paid external LLM API.

Users should still avoid entering sensitive personal information into development or demonstration environments.

📜 Disclaimer

CivicAI is an independent software project created for informational and educational purposes.

It is not affiliated with or endorsed by the Government of India.

CivicAI does not determine official eligibility, approval, selection, or entitlement for any government scheme.

Government schemes, eligibility requirements, deadlines, and procedures may change.

Always verify important information with the relevant official government authority.

👨‍💻 Built With

CivicAI demonstrates practical implementation of:

Retrieval-Augmented Generation
Semantic Search
Vector Databases
Text Embeddings
Local LLM Inference
REST APIs
FastAPI
Frontend Integration
Grounded AI Systems
⭐ Conclusion

CivicAI demonstrates how an AI application can combine modern LLM engineering techniques with structured, domain-specific knowledge to create a useful real-world assistant.

The project focuses on an important principle:

Retrieve relevant information first, then generate an answer grounded in that information.

⭐ If You Find This Project Interesting

Feel free to explore the code, experiment with the RAG pipeline, and extend the knowledge base with additional government schemes.
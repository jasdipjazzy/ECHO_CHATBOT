from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
import google.generativeai as genai
import os
from dotenv import load_dotenv
from pathlib import Path
from contextlib import asynccontextmanager
from rag import vector_store

load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

FRONTEND_DIST = Path(__file__).parent.parent / "frontend" / "dist"

SYSTEM_PROMPT = """You are Echo, a helpful SharePoint assistant for HCL employees.
Answer questions about company policies, procedures, and guidelines.
Always answer based on the provided company documents.
Be concise, accurate, and professional.
If the answer is not in the documents, say: "I don't have information about that. Please contact HR or IT."
Do not make up information."""

@asynccontextmanager
async def lifespan(app: FastAPI):
    vector_store.load()
    yield

app = FastAPI(title="Echo Chatbot API", lifespan=lifespan)
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

class Message(BaseModel):
    role: str
    content: str

class ChatRequest(BaseModel):
    message: str
    history: list[Message] = []

@app.post("/api/chat")
async def chat(req: ChatRequest):
    try:
        docs = vector_store.search(req.message, top_k=3)
        context = "\n\n---\n\n".join([
            f"Document: {d['title']}\nSource: {d['source']}\n\n{d['content']}"
            for d in docs
        ])
        system = f"{SYSTEM_PROMPT}\n\nRELEVANT DOCUMENTS:\n{context}" if docs else SYSTEM_PROMPT
        model = genai.GenerativeModel("gemini-2.0-flash", system_instruction=system)
        history = [{"role": m.role, "parts": [m.content]} for m in req.history if m.role in ("user","model")]
        response = model.start_chat(history=history).send_message(req.message)
        return {
            "reply": response.text,
            "sources": [{"title": d["title"], "source": d["source"], "score": d["score"]} for d in docs]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/health")
async def health():
    return {"status": "ok", "docs_loaded": len(vector_store.documents)}

if FRONTEND_DIST.exists():
    assets = FRONTEND_DIST / "assets"
    if assets.exists():
        app.mount("/assets", StaticFiles(directory=str(assets)), name="assets")

    @app.get("/{full_path:path}")
    async def serve_frontend(full_path: str):
        return FileResponse(str(FRONTEND_DIST / "index.html"))

import json
import numpy as np
import os
from pathlib import Path
from dotenv import load_dotenv
import google.generativeai as genai

load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

DATA_DIR = Path(__file__).parent / "data"
DOCS_PATH = DATA_DIR / "documents.json"
EMBEDDINGS_PATH = DATA_DIR / "embeddings.npy"
DOCSTORE_PATH = DATA_DIR / "docstore.json"

def main():
    with open(DOCS_PATH, encoding="utf-8") as f:
        docs = json.load(f)
    print(f"Computing embeddings for {len(docs)} documents...")
    embeddings = []
    for i, doc in enumerate(docs):
        text = f"{doc['title']}\nSource: {doc['source']}\n\n{doc['content']}"
        result = genai.embed_content(
            model="models/text-embedding-004",
            content=text,
            task_type="retrieval_document",
        )
        embeddings.append(result["embedding"])
        print(f"  [{i+1}/{len(docs)}] {doc['title']}")
    np.save(str(EMBEDDINGS_PATH), np.array(embeddings))
    with open(DOCSTORE_PATH, "w", encoding="utf-8") as f:
        json.dump(docs, f, indent=2)
    print("Done! Run: uvicorn main:app --reload")

if __name__ == "__main__":
    main()

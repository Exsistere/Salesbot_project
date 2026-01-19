from fastapi import FastAPI, UploadFile, File, Form
from fastapi.responses import JSONResponse
from typing import Optional
from RAG import rag
from graph_struct import workflow
import shutil
import os

app = FastAPI()

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

@app.post("/chat")
async def chat(query: str = Form(...),
    file: Optional[UploadFile] = File(None),
):
  pdf_path = None
  if file:
    pdf_path = os.path.join(UPLOAD_DIR, file.filename)
    with open(pdf_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    rag.embed_pdf(pdf_path)
  result = await workflow.Workflow(query)
  print(result)
  return JSONResponse(
        {
            "intent": result["intent_type"],
            "response":result["response"].content,
            "pdf_received": bool(file),
        }
    )
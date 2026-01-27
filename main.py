from fastapi import FastAPI, UploadFile, File, Form
from pydantic import BaseModel
from fastapi.responses import JSONResponse
from typing import Optional, Dict, Any
from RAG import rag
from graph_struct import workflow
import shutil
import os
import json
app = FastAPI()

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)
class ChatRequest(BaseModel):
    query: str
    state: Optional[Dict[str, Any]] = None  # Previous graph state

@app.post("/chat")
async def chat(
   query: str = Form(...),
   state: Optional[str] = Form(None),
   file: Optional[UploadFile] = File(None),
):
  pdf_path = None
  if file:
    pdf_path = os.path.join(UPLOAD_DIR, file.filename)
    with open(pdf_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    rag.embed_pdf(pdf_path)


    
  previous_state = json.loads(state) if state else None
  result = await workflow.Workflow(query, state=previous_state)
  print(result)
  return JSONResponse(
        {
            "intent": result["intent_type"],
            "response":result["response"].content,
            "extracted_details": (
               result["extracted_details"].model_dump()
               if result["extracted_details"]
               else None
            ),
            "pdf_received": bool(file)
        }
    )
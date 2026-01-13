from fastapi import FastAPI, UploadFile, File, Form
from fastapi.responses import JSONResponse
from typing import Optional
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
  result = workflow.Workflow(query)
  return JSONResponse(
        {
            "response": result["intent_type"],
            "pdf_received": bool(file),
        }
    )
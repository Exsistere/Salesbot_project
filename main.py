from fastapi import FastAPI, UploadFile,Body, File, Form, Response
from fastapi.responses import JSONResponse
from typing import Optional
from RAG import rag
from graph_struct import workflow
from stt import transcribe_audio
from gtts import gTTS
import io
import shutil
import os
app = FastAPI()

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)
# class ChatRequest(BaseModel):
#     query: str
#     state: Optional[Dict[str, Any]] = None  # Previous graph state

def text_to_speech_local(text: str) -> bytes:
    tts = gTTS(text)
    audio_bytes_io = io.BytesIO()
    tts.write_to_fp(audio_bytes_io)
    audio_bytes_io.seek(0)
    return audio_bytes_io.read()

@app.post("/tts")
async def tts(payload: dict = Body(...)):
    """
    Expects JSON body: {"text": "Hello world"}
    """
    text = payload.get("text")
    if not text:
        return JSONResponse({"error": "No text provided"}, status_code=400)

    audio_bytes = text_to_speech_local(text)
    return Response(content=audio_bytes, media_type="audio/wav")


@app.post("/chat")
async def chat(
   query: Optional[str] = Form(None),
   #state: Optional[str] = Form(None),
   session_id: str = Form(...),
   audio: Optional[UploadFile] = File(None),
   file: Optional[UploadFile] = File(None),
):
  stt_query = None
  if audio:
    audio_path = os.path.join(UPLOAD_DIR, audio.filename)
    with open(audio_path, "wb") as buffer:
        shutil.copyfileobj(audio.file, buffer)
    try:
        stt_query = transcribe_audio(audio_path)

        if not stt_query:
            return JSONResponse({"error":"No input provided"}, status_code=400)

        query = stt_query
    finally:
       if audio_path and os.path.exists(audio_path):
          os.remove(audio_path)
       

  pdf_path = None
  if file:
    pdf_path = os.path.join(UPLOAD_DIR, file.filename)
    with open(pdf_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    rag.embed_pdf(pdf_path)

    
#   previous_state = json.loads(state) if state else None
#   result = await workflow.Workflow(query, state=previous_state)
  print(query)
  result = await workflow.Workflow(query, session_id=session_id)
  print(result)
  return JSONResponse(
        {
            "intent": result["intent_type"],
            "response":result["response"].content,
            "extracted_details": result.get("extracted_details"),
            "pdf_received": bool(file),
            "audio_recieved": bool(audio),
            "transcribed_text": stt_query
        }
    )
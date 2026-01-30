from faster_whisper import WhisperModel

model = WhisperModel(
    "base",
    device="cpu",     # change to "cuda" if GPU
    compute_type="int8"
)

def transcribe_audio(audio_path: str) -> str:
    segments, _ = model.transcribe(audio_path)
    text = " ".join(segment.text for segment in segments)
    return text.strip()

from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from sqlalchemy.orm import Session
from database import models, database
from api.schemas import ASRResponse
from services.asr.engine import ASREngine
import os
import base64
import tempfile
from uuid import uuid4
from pydantic import BaseModel

router = APIRouter(prefix="/asr", tags=["ASR"])

MAX_AUDIO_BYTES = 20 * 1024 * 1024

# Inicializar motor ASR
asr_engine = ASREngine()

class TranscribeRequest(BaseModel):
    audio_data: str
    format: str = "wav"
    sample_rate: int = 16000
    language: str = "es"

class TranscribeResponse(BaseModel):
    transcription: str
    confidence: float
    language: str

@router.post("/transcribe", response_model=TranscribeResponse)
async def transcribe_audio(request: TranscribeRequest, db: Session = Depends(database.get_db)):
    """Transcribir audio desde base64"""
    try:
        # Decodificar audio base64
        audio_bytes = base64.b64decode(request.audio_data)
        
        if len(audio_bytes) > MAX_AUDIO_BYTES:
            raise HTTPException(413, "Archivo demasiado grande")
        
        # Crear archivo temporal
        with tempfile.NamedTemporaryFile(suffix=f".{request.format}", delete=False) as tmp_file:
            tmp_file.write(audio_bytes)
            tmp_path = tmp_file.name
        
        try:
            # Transcribir usando el motor ASR
            res = asr_engine.transcribe_file(tmp_path, language=request.language)
            
            # Simular confianza basada en la longitud del texto
            confidence = min(0.95, max(0.3, len(res["text"]) / 50.0))
            
            return TranscribeResponse(
                transcription=res["text"],
                confidence=confidence,
                language=request.language
            )
        finally:
            # Limpiar archivo temporal
            if os.path.exists(tmp_path):
                os.remove(tmp_path)
                
    except Exception as e:
        raise HTTPException(500, f"Error en transcripción: {str(e)}")

@router.post("/voice", response_model=ASRResponse)
async def voice_asr(file: UploadFile = File(...), id_sesion: str = None, db: Session = Depends(database.get_db)):
    if file.content_type not in {"audio/wav","audio/x-wav","audio/wave","audio/mpeg","audio/mp3"}:
        raise HTTPException(415, "Formato no soportado")

    data = await file.read()
    if len(data) > MAX_AUDIO_BYTES:
        raise HTTPException(413, "Archivo demasiado grande")

    suffix = os.path.splitext(file.filename or "")[1] or ".tmp"
    tmp = f"/tmp/upload_{uuid4().hex}{suffix}"
    with open(tmp, "wb") as f:
        f.write(data)

    try:
        res = asr_engine.transcribe_file(tmp, language="es")
        # Registrar en la base
        if id_sesion:
            consulta = models.ConsultaVoz(
                id_sesion=id_sesion,
                transcripcion=res["text"],
                intencion="buscar_producto",
                entidades="{}",
                confianza="alta",
                exito=True
            )
            db.add(consulta)
            db.commit()
        return ASRResponse(**res)
    finally:
        os.remove(tmp)

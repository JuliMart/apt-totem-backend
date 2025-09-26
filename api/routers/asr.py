from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from sqlalchemy.orm import Session
from database import models, database
from api.schemas import ASRResponse
from services.asr import engine as asr
import os
from uuid import uuid4

router = APIRouter(prefix="/voice", tags=["ASR"])

MAX_AUDIO_BYTES = 20 * 1024 * 1024

@router.post("/asr", response_model=ASRResponse)
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
        res = asr.transcribe_file(tmp, language="es")
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

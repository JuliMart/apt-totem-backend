from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import models, database
from datetime import datetime

router = APIRouter(prefix="/sesion", tags=["Sesiones"])

@router.post("/start")
def start_session(canal: str = "mixto", db: Session = Depends(database.get_db)):
    sesion = models.Sesion(canal=canal)
    db.add(sesion)
    db.commit()
    db.refresh(sesion)
    return {"id_sesion": sesion.id_sesion, "inicio": sesion.inicio.isoformat()}

@router.post("/end/{id_sesion}")
def end_session(id_sesion: str, db: Session = Depends(database.get_db)):
    sesion = db.query(models.Sesion).filter(models.Sesion.id_sesion == id_sesion).first()
    if not sesion:
        raise HTTPException(404, "Sesión no encontrada")
    sesion.termino = datetime.utcnow()
    db.commit()
    return {"message": "Sesión finalizada", "id_sesion": id_sesion}

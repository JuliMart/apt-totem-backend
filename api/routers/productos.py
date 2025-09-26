from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from database import models, database

router = APIRouter(prefix="/productos", tags=["Productos"])

@router.get("/")
def listar_productos(db: Session = Depends(database.get_db)):
    return db.query(models.Producto).all()

@router.get("/{id_producto}")
def detalle_producto(id_producto: int, db: Session = Depends(database.get_db)):
    p = db.query(models.Producto).filter(models.Producto.id_producto == id_producto).first()
    if not p:
        raise HTTPException(404, "Producto no encontrado")
    return p

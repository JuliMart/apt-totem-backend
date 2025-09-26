from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from database import models, database
from typing import List

router = APIRouter(prefix="/recomendaciones", tags=["Recomendaciones"])

@router.get("/")
def recomendar(
    categoria: str = Query(None, description="Ej: zapatillas"),
    color: str = Query(None, description="Ej: rojo"),
    db: Session = Depends(database.get_db)
):
    query = db.query(models.ProductoVariante).join(models.Producto)

    if categoria:
        query = query.join(models.Categoria).filter(models.Categoria.nombre.ilike(f"%{categoria}%"))

    if color:
        query = query.filter(models.ProductoVariante.color.ilike(f"%{color}%"))

    resultados = query.all()

    return [
        {
            "id_variante": v.id_variante,
            "producto": v.producto.nombre,
            "marca": v.producto.marca,
            "color": v.color,
            "talla": v.talla,
            "precio": v.precio,
            "image_url": v.image_url
        }
        for v in resultados
    ]

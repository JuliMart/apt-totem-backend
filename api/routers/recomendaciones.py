from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session
from database import models, database
from services.recommendation_engine import get_recommendation_engine
from typing import List, Optional

router = APIRouter(prefix="/recomendaciones", tags=["Recomendaciones"])

@router.get("/")
def recomendar(
    categoria: str = Query(None, description="Ej: zapatillas"),
    color: str = Query(None, description="Ej: rojo"),
    marca: str = Query(None, description="Ej: nike"),
    precio_max: float = Query(None, description="Precio máximo"),
    session_id: str = Query(None, description="ID de sesión para tracking"),
    limit: int = Query(10, ge=1, le=50, description="Número de recomendaciones"),
    db: Session = Depends(database.get_db)
):
    """Recomendaciones básicas por filtros con tracking"""
    engine = get_recommendation_engine(db)
    
    if categoria:
        return engine.get_products_by_category(categoria, limit, session_id)
    elif color:
        return engine.get_products_by_color(color, limit, session_id)
    elif marca:
        return engine.get_products_by_brand(marca, limit, session_id)
    elif precio_max:
        return engine.get_products_by_price_range(0, precio_max, limit, session_id)
    else:
        # Si no hay filtros, devolver productos trending
        return engine.get_trending_products(limit=limit, session_id=session_id)

@router.get("/similar/{product_id}")
def productos_similares(
    product_id: int,
    limit: int = Query(5, ge=1, le=20, description="Número de productos similares"),
    db: Session = Depends(database.get_db)
):
    """Obtener productos similares a uno específico"""
    engine = get_recommendation_engine(db)
    return engine.get_similar_products(product_id, limit)

@router.get("/cross-sell/{product_id}")
def productos_complementarios(
    product_id: int,
    limit: int = Query(5, ge=1, le=20, description="Número de productos complementarios"),
    db: Session = Depends(database.get_db)
):
    """Obtener productos complementarios (cross-selling)"""
    engine = get_recommendation_engine(db)
    return engine.get_cross_sell_recommendations(product_id, limit)

@router.get("/personalizadas")
def recomendaciones_personalizadas(
    edad: str = Query(None, description="Rango de edad: 18-25, 26-35, 36-45, 46-55, 55+"),
    genero: str = Query(None, description="masculino, femenino"),
    estilo: str = Query(None, description="casual, formal, deportivo, elegante"),
    color_preferido: str = Query(None, description="Color preferido"),
    limit: int = Query(10, ge=1, le=50, description="Número de recomendaciones"),
    db: Session = Depends(database.get_db)
):
    """Recomendaciones personalizadas basadas en perfil del usuario"""
    engine = get_recommendation_engine(db)
    return engine.get_personalized_recommendations(
        age_range=edad,
        gender=genero,
        clothing_style=estilo,
        color_preference=color_preferido,
        limit=limit
    )

@router.get("/trending")
def productos_trending(
    dias: int = Query(7, ge=1, le=30, description="Días para calcular trending"),
    limit: int = Query(10, ge=1, le=50, description="Número de productos trending"),
    db: Session = Depends(database.get_db)
):
    """Obtener productos trending basados en detecciones recientes"""
    engine = get_recommendation_engine(db)
    return engine.get_trending_products(days=dias, limit=limit)

@router.get("/presupuesto")
def recomendaciones_presupuesto(
    presupuesto_max: float = Query(..., description="Presupuesto máximo"),
    limit: int = Query(10, ge=1, le=50, description="Número de recomendaciones"),
    db: Session = Depends(database.get_db)
):
    """Recomendaciones dentro de un presupuesto"""
    engine = get_recommendation_engine(db)
    return engine.get_budget_recommendations(presupuesto_max, limit)

@router.get("/estacionales")
def recomendaciones_estacionales(
    temporada: str = Query("verano", description="verano, invierno, primavera, otoño"),
    limit: int = Query(10, ge=1, le=50, description="Número de recomendaciones"),
    db: Session = Depends(database.get_db)
):
    """Recomendaciones estacionales"""
    engine = get_recommendation_engine(db)
    return engine.get_seasonal_recommendations(temporada, limit)

@router.get("/categoria/{categoria}")
def productos_por_categoria(
    categoria: str,
    limit: int = Query(10, ge=1, le=50, description="Número de productos"),
    db: Session = Depends(database.get_db)
):
    """Obtener productos por categoría específica"""
    engine = get_recommendation_engine(db)
    return engine.get_products_by_category(categoria, limit)

@router.get("/marca/{marca}")
def productos_por_marca(
    marca: str,
    limit: int = Query(10, ge=1, le=50, description="Número de productos"),
    db: Session = Depends(database.get_db)
):
    """Obtener productos por marca específica"""
    engine = get_recommendation_engine(db)
    return engine.get_products_by_brand(marca, limit)

@router.get("/color/{color}")
def productos_por_color(
    color: str,
    limit: int = Query(10, ge=1, le=50, description="Número de productos"),
    db: Session = Depends(database.get_db)
):
    """Obtener productos por color específico"""
    engine = get_recommendation_engine(db)
    return engine.get_products_by_color(color, limit)

@router.get("/rango-precio")
def productos_por_rango_precio(
    precio_min: float = Query(0, description="Precio mínimo"),
    precio_max: float = Query(..., description="Precio máximo"),
    limit: int = Query(10, ge=1, le=50, description="Número de productos"),
    db: Session = Depends(database.get_db)
):
    """Obtener productos por rango de precio"""
    engine = get_recommendation_engine(db)
    return engine.get_products_by_price_range(precio_min, precio_max, limit)

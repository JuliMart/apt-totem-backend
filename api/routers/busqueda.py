from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session
from database import database
from services.search_engine import get_search_recommendation_engine
from typing import List, Dict, Optional
from datetime import datetime

router = APIRouter(prefix="/busqueda", tags=["Búsqueda"])

@router.get("/")
def buscar_productos(
    q: str = Query(..., description="Término de búsqueda"),
    session_id: str = Query(None, description="ID de sesión para tracking"),
    limit: int = Query(10, ge=1, le=50, description="Número de resultados"),
    db: Session = Depends(database.get_db)
):
    """Buscar productos por texto con scoring inteligente"""
    try:
        search_engine = get_search_recommendation_engine(db)
        resultados = search_engine.search_products(q, limit, session_id)
        
        return {
            "query": q,
            "total_results": len(resultados),
            "session_id": session_id,
            "results": resultados,
            "search_timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error en búsqueda: {str(e)}")

@router.get("/sugerencias")
def obtener_sugerencias_busqueda(
    q: str = Query(..., description="Término de búsqueda para sugerencias"),
    limit: int = Query(5, ge=1, le=20, description="Número de sugerencias"),
    db: Session = Depends(database.get_db)
):
    """Obtener sugerencias de búsqueda basadas en productos disponibles"""
    try:
        search_engine = get_search_recommendation_engine(db)
        sugerencias = search_engine.get_search_suggestions(q, limit)
        
        return {
            "query": q,
            "suggestions": sugerencias,
            "total_suggestions": len(sugerencias)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al obtener sugerencias: {str(e)}")

@router.get("/analytics")
def obtener_analytics_busqueda(
    q: str = Query(..., description="Término de búsqueda para analytics"),
    db: Session = Depends(database.get_db)
):
    """Obtener analytics de una búsqueda específica"""
    try:
        search_engine = get_search_recommendation_engine(db)
        analytics = search_engine.get_search_analytics(q)
        
        return analytics
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al obtener analytics: {str(e)}")

@router.get("/popular")
def obtener_busquedas_populares(
    limit: int = Query(10, ge=1, le=50, description="Número de búsquedas populares"),
    db: Session = Depends(database.get_db)
):
    """Obtener búsquedas más populares (simulado)"""
    try:
        # Por ahora devolvemos búsquedas populares simuladas
        # En el futuro se pueden obtener de logs reales
        busquedas_populares = [
            {"query": "zapatillas", "count": 45, "category": "Zapatillas"},
            {"query": "nike", "count": 38, "category": "Marca"},
            {"query": "chaquetas", "count": 32, "category": "Chaquetas"},
            {"query": "adidas", "count": 28, "category": "Marca"},
            {"query": "poleras", "count": 25, "category": "Poleras"},
            {"query": "azul", "count": 22, "category": "Color"},
            {"query": "pantalones", "count": 20, "category": "Pantalones"},
            {"query": "converse", "count": 18, "category": "Marca"},
            {"query": "rojo", "count": 15, "category": "Color"},
            {"query": "accesorios", "count": 12, "category": "Accesorios"}
        ]
        
        return {
            "popular_searches": busquedas_populares[:limit],
            "total_popular_searches": len(busquedas_populares),
            "period": "últimos 30 días"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al obtener búsquedas populares: {str(e)}")

@router.get("/trending")
def obtener_tendencias_busqueda(
    limit: int = Query(10, ge=1, le=50, description="Número de tendencias"),
    db: Session = Depends(database.get_db)
):
    """Obtener tendencias de búsqueda actuales"""
    try:
        # Por ahora devolvemos tendencias simuladas
        # En el futuro se pueden obtener de análisis de datos reales
        tendencias = [
            {"query": "zapatillas deportivas", "trend": "up", "change": "+25%"},
            {"query": "chaquetas de invierno", "trend": "up", "change": "+18%"},
            {"query": "ropa casual", "trend": "up", "change": "+12%"},
            {"query": "accesorios de moda", "trend": "up", "change": "+8%"},
            {"query": "pantalones jeans", "trend": "stable", "change": "0%"},
            {"query": "poleras básicas", "trend": "down", "change": "-5%"},
            {"query": "zapatos formales", "trend": "down", "change": "-8%"},
            {"query": "ropa de verano", "trend": "down", "change": "-15%"}
        ]
        
        return {
            "trending_searches": tendencias[:limit],
            "total_trends": len(tendencias),
            "period": "última semana",
            "analysis_date": datetime.utcnow().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al obtener tendencias: {str(e)}")

@router.get("/autocomplete")
def autocompletar_busqueda(
    q: str = Query(..., description="Término de búsqueda para autocompletar"),
    limit: int = Query(8, ge=1, le=20, description="Número de sugerencias"),
    db: Session = Depends(database.get_db)
):
    """Autocompletar búsqueda con sugerencias inteligentes"""
    try:
        search_engine = get_search_recommendation_engine(db)
        
        if len(q) < 2:
            return {
                "query": q,
                "suggestions": [],
                "total_suggestions": 0
            }
        
        # Obtener sugerencias
        sugerencias = search_engine.get_search_suggestions(q, limit)
        
        # Formatear sugerencias con información adicional
        sugerencias_formateadas = []
        for sugerencia in sugerencias:
            # Buscar productos que coincidan con la sugerencia
            productos = search_engine.search_products(sugerencia, limit=1)
            
            sugerencias_formateadas.append({
                "text": sugerencia,
                "type": "suggestion",
                "product_count": len(productos),
                "category": productos[0]['categoria'] if productos else None
            })
        
        return {
            "query": q,
            "suggestions": sugerencias_formateadas,
            "total_suggestions": len(sugerencias_formateadas)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error en autocompletar: {str(e)}")

@router.get("/filters")
def obtener_filtros_disponibles(
    q: str = Query(None, description="Término de búsqueda para filtrar opciones"),
    db: Session = Depends(database.get_db)
):
    """Obtener filtros disponibles para una búsqueda"""
    try:
        from database.models import Categoria, Producto, ProductoVariante
        from sqlalchemy import func
        
        # Obtener categorías disponibles
        categorias = db.query(Categoria.nombre).all()
        
        # Obtener marcas disponibles
        marcas = db.query(Producto.marca).distinct().all()
        
        # Obtener colores disponibles
        colores = db.query(ProductoVariante.color).distinct().all()
        
        # Obtener rangos de precio
        precio_min = db.query(func.min(ProductoVariante.precio)).scalar()
        precio_max = db.query(func.max(ProductoVariante.precio)).scalar()
        
        # Filtrar por búsqueda si se proporciona
        if q:
            search_engine = get_search_recommendation_engine(db)
            productos_busqueda = search_engine.search_products(q, limit=100)
            
            # Extraer categorías, marcas y colores de los resultados
            categorias_resultado = list(set([p['categoria'] for p in productos_busqueda]))
            marcas_resultado = list(set([p['marca'] for p in productos_busqueda]))
            colores_resultado = list(set([p['color'] for p in productos_busqueda]))
            
            # Filtrar precios de los resultados
            precios_resultado = [p['precio'] for p in productos_busqueda]
            precio_min_resultado = min(precios_resultado) if precios_resultado else precio_min
            precio_max_resultado = max(precios_resultado) if precios_resultado else precio_max
        else:
            categorias_resultado = [cat.nombre for cat in categorias]
            marcas_resultado = [marca.marca for marca in marcas if marca.marca]
            colores_resultado = [color.color for color in colores if color.color]
            precio_min_resultado = precio_min
            precio_max_resultado = precio_max
        
        return {
            "query": q,
            "filters": {
                "categories": categorias_resultado,
                "brands": marcas_resultado,
                "colors": colores_resultado,
                "price_range": {
                    "min": precio_min_resultado,
                    "max": precio_max_resultado
                }
            },
            "total_options": {
                "categories": len(categorias_resultado),
                "brands": len(marcas_resultado),
                "colors": len(colores_resultado)
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al obtener filtros: {str(e)}")

@router.get("/health")
def verificar_salud_busqueda(db: Session = Depends(database.get_db)):
    """Verificar el estado del sistema de búsqueda"""
    try:
        search_engine = get_search_recommendation_engine(db)
        
        # Probar búsqueda básica
        test_results = search_engine.search_products("test", limit=1)
        
        # Obtener estadísticas de la base de datos
        from database.models import Producto, ProductoVariante, Categoria
        
        total_productos = db.query(Producto).count()
        total_variantes = db.query(ProductoVariante).count()
        total_categorias = db.query(Categoria).count()
        
        return {
            "status": "healthy",
            "search_engine": "operational",
            "database_stats": {
                "total_productos": total_productos,
                "total_variantes": total_variantes,
                "total_categorias": total_categorias
            },
            "test_search": "successful",
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "search_engine": "error",
            "error": str(e),
            "timestamp": datetime.utcnow().isoformat()
        }

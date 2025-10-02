from fastapi import APIRouter, HTTPException, Depends, Query
from sqlalchemy.orm import Session
from typing import List, Dict, Optional
from database import database
from services.retail_api import get_retail_api_client, sync_external_data
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/retail-api", tags=["Retail API"])

@router.get("/categories")
def get_external_categories():
    """Obtener categorías de la API externa"""
    try:
        client = get_retail_api_client()
        categories = client.service.get_categories()
        return {"categories": categories, "count": len(categories)}
    except Exception as e:
        logger.error(f"Error al obtener categorías externas: {e}")
        raise HTTPException(status_code=500, detail="Error al obtener categorías externas")

@router.get("/products")
def get_external_products(
    limit: int = Query(20, ge=1, le=100, description="Número de productos a obtener"),
    category: Optional[str] = Query(None, description="Filtrar por categoría")
):
    """Obtener productos de la API externa"""
    try:
        client = get_retail_api_client()
        
        if category:
            products = client.service.get_products_by_category(category)
        else:
            products = client.service.get_products(limit)
        
        return {
            "products": products,
            "count": len(products),
            "category": category,
            "limit": limit
        }
    except Exception as e:
        logger.error(f"Error al obtener productos externos: {e}")
        raise HTTPException(status_code=500, detail="Error al obtener productos externos")

@router.get("/products/{product_id}")
def get_external_product(product_id: int):
    """Obtener un producto específico de la API externa"""
    try:
        client = get_retail_api_client()
        product = client.service.get_product_by_id(product_id)
        
        if not product:
            raise HTTPException(status_code=404, detail="Producto no encontrado")
        
        return product
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error al obtener producto {product_id}: {e}")
        raise HTTPException(status_code=500, detail="Error al obtener producto")

@router.get("/search")
def search_external_products(
    q: str = Query(..., description="Término de búsqueda"),
    category: Optional[str] = Query(None, description="Filtrar por categoría")
):
    """Buscar productos en la API externa"""
    try:
        client = get_retail_api_client()
        results = client.service.search_products(q, category)
        
        return {
            "query": q,
            "category": category,
            "results": results,
            "count": len(results)
        }
    except Exception as e:
        logger.error(f"Error en búsqueda: {e}")
        raise HTTPException(status_code=500, detail="Error en búsqueda")

@router.get("/recommendations/{product_id}")
def get_product_recommendations(
    product_id: int,
    limit: int = Query(5, ge=1, le=20, description="Número de recomendaciones")
):
    """Obtener recomendaciones basadas en un producto"""
    try:
        client = get_retail_api_client()
        recommendations = client.service.get_product_recommendations(product_id, limit)
        
        return {
            "base_product_id": product_id,
            "recommendations": recommendations,
            "count": len(recommendations)
        }
    except Exception as e:
        logger.error(f"Error al obtener recomendaciones: {e}")
        raise HTTPException(status_code=500, detail="Error al obtener recomendaciones")

@router.post("/sync")
def sync_external_data_to_db(
    products_limit: int = Query(50, ge=1, le=100, description="Límite de productos a sincronizar"),
    db: Session = Depends(database.get_db)
):
    """Sincronizar datos de la API externa a la base de datos local"""
    try:
        result = sync_external_data(db, products_limit)
        
        return {
            "message": "Sincronización completada",
            "categories_synced": result["categories_synced"],
            "products_synced": result["products_synced"],
            "products_limit": products_limit
        }
    except Exception as e:
        logger.error(f"Error en sincronización: {e}")
        raise HTTPException(status_code=500, detail="Error en sincronización")

@router.post("/sync-categories")
def sync_categories_to_db(db: Session = Depends(database.get_db)):
    """Sincronizar solo las categorías de la API externa"""
    try:
        client = get_retail_api_client()
        categories_synced = client.service.sync_categories_to_db(db)
        
        return {
            "message": "Categorías sincronizadas",
            "categories_synced": categories_synced
        }
    except Exception as e:
        logger.error(f"Error al sincronizar categorías: {e}")
        raise HTTPException(status_code=500, detail="Error al sincronizar categorías")

@router.post("/sync-products")
def sync_products_to_db(
    limit: int = Query(50, ge=1, le=100, description="Límite de productos a sincronizar"),
    db: Session = Depends(database.get_db)
):
    """Sincronizar solo los productos de la API externa"""
    try:
        client = get_retail_api_client()
        products_synced = client.service.sync_products_to_db(db, limit)
        
        return {
            "message": "Productos sincronizados",
            "products_synced": products_synced,
            "limit": limit
        }
    except Exception as e:
        logger.error(f"Error al sincronizar productos: {e}")
        raise HTTPException(status_code=500, detail="Error al sincronizar productos")

@router.get("/health")
def check_api_health():
    """Verificar el estado de la API externa"""
    try:
        client = get_retail_api_client()
        # Intentar obtener categorías para verificar conectividad
        categories = client.service.get_categories()
        
        return {
            "status": "healthy",
            "external_api": "fakestoreapi.com",
            "categories_available": len(categories),
            "message": "API externa funcionando correctamente"
        }
    except Exception as e:
        logger.error(f"Error en health check: {e}")
        return {
            "status": "unhealthy",
            "external_api": "fakestoreapi.com",
            "error": str(e),
            "message": "Error de conectividad con API externa"
        }


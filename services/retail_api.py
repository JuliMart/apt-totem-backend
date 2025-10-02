"""
Servicio para integrar con APIs retail externas
"""
import requests
import json
from typing import List, Dict, Optional
from datetime import datetime
from sqlalchemy.orm import Session
from database.models import Categoria, Producto, ProductoVariante
import logging

logger = logging.getLogger(__name__)

class RetailAPIService:
    """Servicio para integrar con APIs de retail externas"""
    
    def __init__(self):
        self.base_url = "https://fakestoreapi.com"
        self.timeout = 10
    
    def get_categories(self) -> List[str]:
        """Obtener categorías de la API externa"""
        try:
            response = requests.get(f"{self.base_url}/products/categories", timeout=self.timeout)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            logger.error(f"Error al obtener categorías: {e}")
            return []
    
    def get_products(self, limit: int = 20) -> List[Dict]:
        """Obtener productos de la API externa"""
        try:
            response = requests.get(f"{self.base_url}/products?limit={limit}", timeout=self.timeout)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            logger.error(f"Error al obtener productos: {e}")
            return []
    
    def get_product_by_id(self, product_id: int) -> Optional[Dict]:
        """Obtener un producto específico por ID"""
        try:
            response = requests.get(f"{self.base_url}/products/{product_id}", timeout=self.timeout)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            logger.error(f"Error al obtener producto {product_id}: {e}")
            return None
    
    def get_products_by_category(self, category: str) -> List[Dict]:
        """Obtener productos por categoría"""
        try:
            response = requests.get(f"{self.base_url}/products/category/{category}", timeout=self.timeout)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            logger.error(f"Error al obtener productos de categoría {category}: {e}")
            return []
    
    def sync_categories_to_db(self, db: Session) -> int:
        """Sincronizar categorías de la API a la base de datos local"""
        api_categories = self.get_categories()
        created_count = 0
        
        for cat_name in api_categories:
            # Normalizar nombre de categoría
            normalized_name = cat_name.title()
            
            existing = db.query(Categoria).filter(Categoria.nombre == normalized_name).first()
            if not existing:
                categoria = Categoria(nombre=normalized_name)
                db.add(categoria)
                created_count += 1
        
        db.commit()
        logger.info(f"Sincronizadas {created_count} nuevas categorías")
        return created_count
    
    def sync_products_to_db(self, db: Session, limit: int = 50) -> int:
        """Sincronizar productos de la API a la base de datos local"""
        api_products = self.get_products(limit)
        created_count = 0
        
        for product_data in api_products:
            # Buscar o crear categoría
            categoria = db.query(Categoria).filter(
                Categoria.nombre == product_data['category'].title()
            ).first()
            
            if not categoria:
                categoria = Categoria(nombre=product_data['category'].title())
                db.add(categoria)
                db.flush()
            
            # Verificar si el producto ya existe
            existing_product = db.query(Producto).filter(
                Producto.nombre == product_data['title']
            ).first()
            
            if not existing_product:
                # Crear producto
                producto = Producto(
                    nombre=product_data['title'],
                    id_categoria=categoria.id_categoria,
                    marca="API Externa"  # La API no tiene marca específica
                )
                db.add(producto)
                db.flush()
                
                # Crear variante (la API solo tiene un producto por item)
                variante = ProductoVariante(
                    id_producto=producto.id_producto,
                    sku=f"API-{product_data['id']}",
                    talla="M",  # Talla por defecto
                    color="N/A",  # Color no especificado en la API
                    precio=product_data['price'],
                    image_url=product_data['image']
                )
                db.add(variante)
                created_count += 1
        
        db.commit()
        logger.info(f"Sincronizados {created_count} nuevos productos")
        return created_count
    
    def search_products(self, query: str, category: Optional[str] = None) -> List[Dict]:
        """Buscar productos en la API externa"""
        try:
            if category:
                products = self.get_products_by_category(category)
            else:
                products = self.get_products(100)  # Obtener más productos para buscar
            
            # Filtrar por query (búsqueda simple por título)
            filtered_products = [
                p for p in products 
                if query.lower() in p['title'].lower()
            ]
            
            return filtered_products[:20]  # Limitar resultados
            
        except Exception as e:
            logger.error(f"Error en búsqueda: {e}")
            return []
    
    def get_product_recommendations(self, product_id: int, limit: int = 5) -> List[Dict]:
        """Obtener recomendaciones basadas en un producto"""
        try:
            # Obtener el producto base
            base_product = self.get_product_by_id(product_id)
            if not base_product:
                return []
            
            # Obtener productos de la misma categoría
            category_products = self.get_products_by_category(base_product['category'])
            
            # Filtrar el producto actual y obtener recomendaciones
            recommendations = [
                p for p in category_products 
                if p['id'] != product_id
            ]
            
            return recommendations[:limit]
            
        except Exception as e:
            logger.error(f"Error al obtener recomendaciones: {e}")
            return []

class RetailAPIClient:
    """Cliente simplificado para usar el servicio de retail API"""
    
    def __init__(self):
        self.service = RetailAPIService()
    
    def sync_all_data(self, db: Session, products_limit: int = 50) -> Dict[str, int]:
        """Sincronizar todos los datos de la API externa"""
        logger.info("Iniciando sincronización completa con API externa...")
        
        categories_synced = self.service.sync_categories_to_db(db)
        products_synced = self.service.sync_products_to_db(db, products_limit)
        
        return {
            "categories_synced": categories_synced,
            "products_synced": products_synced
        }
    
    def search_and_sync(self, db: Session, query: str, category: Optional[str] = None) -> List[Dict]:
        """Buscar productos en la API y opcionalmente sincronizar"""
        results = self.service.search_products(query, category)
        
        # Opcionalmente sincronizar resultados encontrados
        for product in results[:5]:  # Sincronizar solo los primeros 5
            self.service.sync_products_to_db(db, 1)  # Sincronizar uno por uno
        
        return results

# Función de utilidad para usar desde otros módulos
def get_retail_api_client() -> RetailAPIClient:
    """Obtener instancia del cliente de retail API"""
    return RetailAPIClient()

def sync_external_data(db: Session, products_limit: int = 50) -> Dict[str, int]:
    """Función de conveniencia para sincronizar datos externos"""
    client = get_retail_api_client()
    return client.sync_all_data(db, products_limit)


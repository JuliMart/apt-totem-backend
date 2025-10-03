"""
Sistema de recomendaciones basado en búsqueda de texto
"""
import re
from typing import List, Dict, Optional
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func
from database.models import Producto, ProductoVariante, Categoria
from datetime import datetime
import time

class SearchRecommendationEngine:
    """Motor de recomendaciones basado en búsqueda de texto"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def search_products(self, query: str, limit: int = 10, session_id: Optional[str] = None) -> List[Dict]:
        """Buscar productos por texto con scoring inteligente"""
        start_time = time.time()
        
        if not query or len(query.strip()) < 2:
            return []
        
        query_clean = query.strip().lower()
        
        # Dividir la búsqueda en términos
        terms = re.findall(r'\b\w+\b', query_clean)
        
        if not terms:
            return []
        
        # Buscar productos que coincidan con los términos
        productos = []
        
        # Buscar por nombre de producto (mayor peso)
        for term in terms:
            productos_nombre = self.db.query(ProductoVariante).join(Producto).filter(
                func.lower(Producto.nombre).contains(term)
            ).all()
            productos.extend(productos_nombre)
        
        # Buscar por marca (peso medio)
        for term in terms:
            productos_marca = self.db.query(ProductoVariante).join(Producto).filter(
                func.lower(Producto.marca).contains(term)
            ).all()
            productos.extend(productos_marca)
        
        # Buscar por categoría
        for term in terms:
            productos_categoria = self.db.query(ProductoVariante).join(Producto).join(Categoria).filter(
                func.lower(Categoria.nombre).contains(term)
            ).all()
            productos.extend(productos_categoria)
        
        # Buscar por color
        for term in terms:
            productos_color = self.db.query(ProductoVariante).filter(
                func.lower(ProductoVariante.color).contains(term)
            ).all()
            productos.extend(productos_color)
        
        # Eliminar duplicados y calcular scores
        unique_products = {}
        for producto in productos:
            variant_id = producto.id_variante
            
            if variant_id not in unique_products:
                score = self._calculate_search_score(producto, terms, query_clean)
                unique_products[variant_id] = {
                    'producto': producto,
                    'score': score
                }
            else:
                # Si ya existe, aumentar el score
                unique_products[variant_id]['score'] += self._calculate_search_score(producto, terms, query_clean)
        
        # Ordenar por score y limitar resultados
        sorted_products = sorted(unique_products.values(), key=lambda x: x['score'], reverse=True)
        top_products = [item['producto'] for item in sorted_products[:limit]]
        
        # Formatear resultados
        formatted_products = self._format_products(top_products)
        
        # Agregar información de búsqueda
        for i, product in enumerate(formatted_products):
            product['search_score'] = sorted_products[i]['score']
            product['search_rank'] = i + 1
        
        generation_time_ms = int((time.time() - start_time) * 1000)
        
        # Trackear la búsqueda si hay session_id
        if session_id:
            from services.recommendation_tracker import get_recommendation_tracker
            tracker = get_recommendation_tracker(self.db)
            tracker.track_recommendation_generation(
                session_id=session_id,
                recommendation_type="busqueda",
                filters_applied={"query": query, "terms": terms},
                algorithm_used="search_engine",
                recommended_products=formatted_products,
                generation_time_ms=generation_time_ms
            )
        
        return formatted_products
    
    def _calculate_search_score(self, producto: ProductoVariante, terms: List[str], full_query: str) -> float:
        """Calcular score de relevancia para un producto"""
        score = 0.0
        
        # Score por nombre exacto
        if full_query in producto.producto.nombre.lower():
            score += 10.0
        
        # Score por términos en nombre
        for term in terms:
            if term in producto.producto.nombre.lower():
                score += 5.0
        
        # Score por marca
        for term in terms:
            if term in producto.producto.marca.lower():
                score += 3.0
        
        # Score por categoría
        for term in terms:
            if term in producto.producto.categoria.nombre.lower():
                score += 2.0
        
        # Score por color
        for term in terms:
            if term in producto.color.lower():
                score += 1.0
        
        # Bonus por precio (productos más baratos tienen ligera ventaja)
        if producto.precio < 50000:
            score += 0.5
        
        return score
    
    def get_search_suggestions(self, query: str, limit: int = 5) -> List[str]:
        """Obtener sugerencias de búsqueda basadas en productos disponibles"""
        if len(query) < 2:
            return []
        
        suggestions = set()
        query_lower = query.lower()
        
        # Sugerencias de nombres de productos
        productos = self.db.query(Producto.nombre).filter(
            func.lower(Producto.nombre).contains(query_lower)
        ).limit(10).all()
        
        for producto in productos:
            # Extraer palabras relevantes del nombre
            words = re.findall(r'\b\w+\b', producto.nombre.lower())
            for word in words:
                if word.startswith(query_lower) and len(word) > len(query_lower):
                    suggestions.add(word)
        
        # Sugerencias de marcas
        marcas = self.db.query(Producto.marca).filter(
            func.lower(Producto.marca).contains(query_lower)
        ).limit(5).all()
        
        for marca in marcas:
            if marca.marca.lower().startswith(query_lower):
                suggestions.add(marca.marca)
        
        # Sugerencias de categorías
        categorias = self.db.query(Categoria.nombre).filter(
            func.lower(Categoria.nombre).contains(query_lower)
        ).limit(5).all()
        
        for categoria in categorias:
            if categoria.nombre.lower().startswith(query_lower):
                suggestions.add(categoria.nombre)
        
        # Sugerencias de colores
        colores = self.db.query(ProductoVariante.color).filter(
            func.lower(ProductoVariante.color).contains(query_lower)
        ).limit(5).all()
        
        for color in colores:
            if color.color.lower().startswith(query_lower):
                suggestions.add(color.color)
        
        return list(suggestions)[:limit]
    
    def get_search_analytics(self, query: str) -> Dict:
        """Obtener analytics de una búsqueda específica"""
        # Buscar productos sin limitar para obtener estadísticas
        productos = self.search_products(query, limit=100)
        
        if not productos:
            return {
                "query": query,
                "total_results": 0,
                "categories_found": [],
                "brands_found": [],
                "price_range": {"min": 0, "max": 0, "avg": 0},
                "search_quality": "no_results"
            }
        
        # Analizar categorías encontradas
        categories = {}
        brands = {}
        prices = []
        
        for producto in productos:
            # Categorías
            cat = producto['categoria']
            categories[cat] = categories.get(cat, 0) + 1
            
            # Marcas
            brand = producto['marca']
            brands[brand] = brands.get(brand, 0) + 1
            
            # Precios
            prices.append(producto['precio'])
        
        # Calcular estadísticas de precio
        price_stats = {
            "min": min(prices) if prices else 0,
            "max": max(prices) if prices else 0,
            "avg": sum(prices) / len(prices) if prices else 0
        }
        
        # Determinar calidad de búsqueda
        search_quality = "excellent" if len(productos) >= 10 else "good" if len(productos) >= 5 else "limited"
        
        return {
            "query": query,
            "total_results": len(productos),
            "categories_found": list(categories.keys()),
            "brands_found": list(brands.keys()),
            "price_range": price_stats,
            "search_quality": search_quality,
            "top_categories": sorted(categories.items(), key=lambda x: x[1], reverse=True)[:3],
            "top_brands": sorted(brands.items(), key=lambda x: x[1], reverse=True)[:3]
        }
    
    def _format_products(self, productos: List[ProductoVariante]) -> List[Dict]:
        """Formatear productos para respuesta"""
        return [
            {
                "id_variante": p.id_variante,
                "id_producto": p.id_producto,
                "producto": p.producto.nombre,
                "marca": p.producto.marca,
                "categoria": p.producto.categoria.nombre,
                "sku": p.sku,
                "color": p.color,
                "talla": p.talla,
                "precio": p.precio,
                "image_url": p.image_url,
                "created_at": p.created_at.isoformat() if p.created_at else None
            }
            for p in productos
        ]

def get_search_recommendation_engine(db: Session) -> SearchRecommendationEngine:
    """Obtener instancia del motor de búsqueda"""
    return SearchRecommendationEngine(db)



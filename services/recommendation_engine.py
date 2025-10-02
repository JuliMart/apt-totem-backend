"""
Sistema de recomendaciones basado en productos disponibles con tracking
"""
import random
import time
from typing import List, Dict, Optional
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from database.models import Producto, ProductoVariante, Categoria, Deteccion, ConsultaVoz
from datetime import datetime, timedelta
from .recommendation_tracker import get_recommendation_tracker

class RecommendationEngine:
    """Motor de recomendaciones basado en productos disponibles con tracking completo"""
    
    def __init__(self, db: Session):
        self.db = db
        self.tracker = get_recommendation_tracker(db)
    
    def _track_recommendation(self, session_id: str, recommendation_type: str, 
                             filters_applied: Dict, algorithm_used: str, 
                             recommended_products: List[Dict], generation_time_ms: int) -> None:
        """Método helper para trackear recomendaciones"""
        if session_id:
            self.tracker.track_recommendation_generation(
                session_id=session_id,
                recommendation_type=recommendation_type,
                filters_applied=filters_applied,
                algorithm_used=algorithm_used,
                recommended_products=recommended_products,
                generation_time_ms=generation_time_ms
            )
    
    def get_products_by_category(self, category_name: str, limit: int = 10, session_id: Optional[str] = None) -> List[Dict]:
        """Obtener productos por categoría con tracking"""
        start_time = time.time()
        
        productos = self.db.query(ProductoVariante).join(Producto).join(Categoria).filter(
            Categoria.nombre.ilike(f"%{category_name}%")
        ).limit(limit).all()
        
        formatted_products = self._format_products(productos)
        generation_time_ms = int((time.time() - start_time) * 1000)
        
        self._track_recommendation(
            session_id, "categoria", {"categoria": category_name}, 
            "category_filter", formatted_products, generation_time_ms
        )
        
        return formatted_products
    
    def get_products_by_color(self, color: str, limit: int = 10, session_id: Optional[str] = None) -> List[Dict]:
        """Obtener productos por color con tracking"""
        start_time = time.time()
        
        productos = self.db.query(ProductoVariante).filter(
            ProductoVariante.color.ilike(f"%{color}%")
        ).limit(limit).all()
        
        formatted_products = self._format_products(productos)
        generation_time_ms = int((time.time() - start_time) * 1000)
        
        self._track_recommendation(
            session_id, "color", {"color": color}, 
            "color_filter", formatted_products, generation_time_ms
        )
        
        return formatted_products
    
    def get_products_by_price_range(self, min_price: float, max_price: float, limit: int = 10, session_id: Optional[str] = None) -> List[Dict]:
        """Obtener productos por rango de precio con tracking"""
        start_time = time.time()
        
        productos = self.db.query(ProductoVariante).filter(
            and_(
                ProductoVariante.precio >= min_price,
                ProductoVariante.precio <= max_price
            )
        ).limit(limit).all()
        
        formatted_products = self._format_products(productos)
        generation_time_ms = int((time.time() - start_time) * 1000)
        
        self._track_recommendation(
            session_id, "precio", {"min_price": min_price, "max_price": max_price}, 
            "price_filter", formatted_products, generation_time_ms
        )
        
        return formatted_products
    
    def get_products_by_brand(self, brand: str, limit: int = 10, session_id: Optional[str] = None) -> List[Dict]:
        """Obtener productos por marca con tracking"""
        start_time = time.time()
        
        productos = self.db.query(ProductoVariante).join(Producto).filter(
            Producto.marca.ilike(f"%{brand}%")
        ).limit(limit).all()
        
        formatted_products = self._format_products(productos)
        generation_time_ms = int((time.time() - start_time) * 1000)
        
        self._track_recommendation(
            session_id, "marca", {"marca": brand}, 
            "brand_filter", formatted_products, generation_time_ms
        )
        
        return formatted_products
    
    def get_similar_products(self, product_id: int, limit: int = 5, session_id: Optional[str] = None) -> List[Dict]:
        """Obtener productos similares con tracking"""
        start_time = time.time()
        
        # Obtener el producto base
        base_product = self.db.query(ProductoVariante).filter(
            ProductoVariante.id_variante == product_id
        ).first()
        
        if not base_product:
            return []
        
        # Buscar productos similares en la misma categoría
        similar_products = self.db.query(ProductoVariante).join(Producto).filter(
            and_(
                Producto.id_categoria == base_product.producto.id_categoria,
                ProductoVariante.id_variante != product_id
            )
        ).limit(limit).all()
        
        formatted_products = self._format_products(similar_products)
        generation_time_ms = int((time.time() - start_time) * 1000)
        
        self._track_recommendation(
            session_id, "similar", {"base_product_id": product_id}, 
            "similar_products", formatted_products, generation_time_ms
        )
        
        return formatted_products
    
    def get_trending_products(self, days: int = 7, limit: int = 10, session_id: Optional[str] = None) -> List[Dict]:
        """Obtener productos trending con tracking"""
        start_time = time.time()
        
        # Obtener prendas detectadas en los últimos días
        recent_detections = self.db.query(Deteccion).filter(
            Deteccion.fecha_hora >= datetime.utcnow() - timedelta(days=days)
        ).all()
        
        # Contar frecuencia de prendas detectadas
        clothing_counts = {}
        for detection in recent_detections:
            if detection.prenda:
                clothing_counts[detection.prenda] = clothing_counts.get(detection.prenda, 0) + 1
        
        # Mapear prendas a categorías
        clothing_to_category = {
            'zapatillas': 'Zapatillas',
            'polera': 'Poleras',
            'chaqueta': 'Chaquetas',
            'pantalón': 'Pantalones',
            'vestido': 'Vestidos',
            'gorro': 'Gorros',
            'gafas': 'Gafas'
        }
        
        # Obtener productos de categorías trending
        trending_products = []
        for clothing, count in sorted(clothing_counts.items(), key=lambda x: x[1], reverse=True):
            if clothing in clothing_to_category:
                category_products = self.get_products_by_category(
                    clothing_to_category[clothing], 
                    limit=3,
                    session_id=None  # Evitar tracking anidado
                )
                trending_products.extend(category_products)
        
        final_products = trending_products[:limit]
        generation_time_ms = int((time.time() - start_time) * 1000)
        
        self._track_recommendation(
            session_id, "trending", {"days": days}, 
            "trending_analysis", final_products, generation_time_ms
        )
        
        return final_products
    
    def get_personalized_recommendations(self, 
                                      age_range: Optional[str] = None,
                                      gender: Optional[str] = None,
                                      clothing_style: Optional[str] = None,
                                      color_preference: Optional[str] = None,
                                      limit: int = 10,
                                      session_id: Optional[str] = None) -> List[Dict]:
        """Obtener recomendaciones personalizadas con tracking"""
        start_time = time.time()
        
        # Lógica de recomendación basada en edad
        if age_range:
            if age_range in ["18-25", "26-35"]:
                # Jóvenes: productos casuales y deportivos
                categories = ["Zapatillas", "Poleras", "Accesorios"]
                brands = ["Nike", "Adidas", "Converse", "Vans"]
            elif age_range in ["36-45", "46-55"]:
                # Adultos: productos profesionales y elegantes
                categories = ["Chaquetas", "Pantalones", "Accesorios"]
                brands = ["Hugo Boss", "Ralph Lauren", "Tommy Hilfiger", "Lacoste"]
            else:
                # Mayores: productos clásicos y cómodos
                categories = ["Chaquetas", "Pantalones", "Accesorios"]
                brands = ["Ralph Lauren", "Lacoste", "Hugo Boss"]
        else:
            categories = ["Zapatillas", "Poleras", "Chaquetas", "Pantalones"]
            brands = ["Nike", "Adidas", "Ralph Lauren", "Hugo Boss"]
        
        # Obtener productos de categorías recomendadas
        recommended_products = []
        for category in categories[:2]:  # Máximo 2 categorías
            products = self.get_products_by_category(category, limit=3, session_id=None)
            recommended_products.extend(products)
        
        # Filtrar por marca si se especifica
        if brands:
            brand_products = []
            for brand in brands[:2]:  # Máximo 2 marcas
                products = self.get_products_by_brand(brand, limit=2, session_id=None)
                brand_products.extend(products)
            recommended_products.extend(brand_products)
        
        # Filtrar por color si se especifica
        if color_preference:
            color_products = self.get_products_by_color(color_preference, limit=5, session_id=None)
            recommended_products.extend(color_products)
        
        # Eliminar duplicados y limitar resultados
        unique_products = []
        seen_ids = set()
        for product in recommended_products:
            if product['id_variante'] not in seen_ids:
                unique_products.append(product)
                seen_ids.add(product['id_variante'])
        
        final_products = unique_products[:limit]
        generation_time_ms = int((time.time() - start_time) * 1000)
        
        self._track_recommendation(
            session_id, "personalizada", {
                "age_range": age_range,
                "gender": gender,
                "clothing_style": clothing_style,
                "color_preference": color_preference
            }, 
            "personalized_ml", final_products, generation_time_ms
        )
        
        return final_products
    
    def get_cross_sell_recommendations(self, product_id: int, limit: int = 5, session_id: Optional[str] = None) -> List[Dict]:
        """Obtener recomendaciones de productos complementarios con tracking"""
        start_time = time.time()
        
        # Obtener el producto base
        base_product = self.db.query(ProductoVariante).filter(
            ProductoVariante.id_variante == product_id
        ).first()
        
        if not base_product:
            return []
        
        # Lógica de cross-selling basada en categoría
        cross_sell_map = {
            "Zapatillas": ["Poleras", "Pantalones", "Accesorios"],
            "Poleras": ["Pantalones", "Chaquetas", "Accesorios"],
            "Chaquetas": ["Poleras", "Pantalones", "Accesorios"],
            "Pantalones": ["Poleras", "Chaquetas", "Zapatillas"],
            "Accesorios": ["Poleras", "Chaquetas", "Pantalones"]
        }
        
        base_category = base_product.producto.categoria.nombre
        recommended_categories = cross_sell_map.get(base_category, ["Poleras", "Accesorios"])
        
        cross_sell_products = []
        for category in recommended_categories:
            products = self.get_products_by_category(category, limit=2, session_id=None)
            cross_sell_products.extend(products)
        
        final_products = cross_sell_products[:limit]
        generation_time_ms = int((time.time() - start_time) * 1000)
        
        self._track_recommendation(
            session_id, "cross_sell", {"base_product_id": product_id}, 
            "cross_selling", final_products, generation_time_ms
        )
        
        return final_products
    
    def get_budget_recommendations(self, max_budget: float, limit: int = 10, session_id: Optional[str] = None) -> List[Dict]:
        """Obtener recomendaciones dentro de un presupuesto con tracking"""
        start_time = time.time()
        
        # Obtener productos por rango de precio
        products = self.get_products_by_price_range(0, max_budget, limit, session_id=None)
        
        # Ordenar por mejor relación calidad-precio (precio más bajo primero)
        products.sort(key=lambda x: x['precio'])
        
        final_products = products[:limit]
        generation_time_ms = int((time.time() - start_time) * 1000)
        
        self._track_recommendation(
            session_id, "presupuesto", {"max_budget": max_budget}, 
            "budget_filter", final_products, generation_time_ms
        )
        
        return final_products
    
    def get_seasonal_recommendations(self, season: str = "verano", limit: int = 10, session_id: Optional[str] = None) -> List[Dict]:
        """Obtener recomendaciones estacionales con tracking"""
        start_time = time.time()
        
        seasonal_categories = {
            "verano": ["Poleras", "Vestidos", "Accesorios"],
            "invierno": ["Chaquetas", "Pantalones", "Accesorios"],
            "primavera": ["Poleras", "Pantalones", "Accesorios"],
            "otoño": ["Chaquetas", "Pantalones", "Accesorios"]
        }
        
        categories = seasonal_categories.get(season.lower(), ["Poleras", "Accesorios"])
        seasonal_products = []
        
        for category in categories:
            products = self.get_products_by_category(category, limit=4, session_id=None)
            seasonal_products.extend(products)
        
        final_products = seasonal_products[:limit]
        generation_time_ms = int((time.time() - start_time) * 1000)
        
        self._track_recommendation(
            session_id, "estacional", {"season": season}, 
            "seasonal_filter", final_products, generation_time_ms
        )
        
        return final_products
    
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

def get_recommendation_engine(db: Session) -> RecommendationEngine:
    """Obtener instancia del motor de recomendaciones"""
    return RecommendationEngine(db)
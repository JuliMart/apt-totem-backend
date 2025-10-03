"""
Servicio de tracking para recomendaciones y métricas
"""
import json
import time
from typing import List, Dict, Optional
from datetime import datetime
from sqlalchemy.orm import Session
from database.models import (
    RecomendacionSesion, RecomendacionItem, InteraccionUsuario, 
    MetricasSesion, Sesion, ProductoVariante
)

class RecommendationTracker:
    """Servicio para trackear recomendaciones y generar métricas"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def track_recommendation_generation(self, 
                                      session_id: str,
                                      recommendation_type: str,
                                      filters_applied: Dict,
                                      algorithm_used: str,
                                      recommended_products: List[Dict],
                                      generation_time_ms: int) -> int:
        """Registrar la generación de una recomendación"""
        
        # Crear registro de recomendación
        recomendacion = RecomendacionSesion(
            id_sesion=session_id,
            tipo_recomendacion=recommendation_type,
            filtros_aplicados=json.dumps(filters_applied),
            algoritmo_usado=algorithm_used,
            total_productos_recomendados=len(recommended_products),
            tiempo_generacion_ms=generation_time_ms
        )
        
        self.db.add(recomendacion)
        self.db.flush()  # Para obtener el ID
        
        # Crear items de recomendación
        for i, product in enumerate(recommended_products):
            item = RecomendacionItem(
                id_recomendacion=recomendacion.id_recomendacion,
                id_variante=product['id_variante'],
                posicion=i + 1,
                score_recomendacion=product.get('score', 1.0),
                fue_mostrado=False  # Se actualizará cuando se muestre
            )
            self.db.add(item)
        
        self.db.commit()
        return recomendacion.id_recomendacion
    
    def track_product_view(self, 
                          session_id: str,
                          variant_id: int,
                          recommendation_id: Optional[int] = None,
                          view_duration_seconds: float = 0) -> None:
        """Registrar cuando un producto es visto"""
        
        # Registrar interacción de vista
        interaccion = InteraccionUsuario(
            id_sesion=session_id,
            tipo_interaccion="view",
            id_variante=variant_id,
            metadata_interaccion=json.dumps({
                "recommendation_id": recommendation_id,
                "view_duration": view_duration_seconds
            }),
            duracion_segundos=view_duration_seconds
        )
        self.db.add(interaccion)
        
        # Si es parte de una recomendación, marcar como mostrado
        if recommendation_id:
            item = self.db.query(RecomendacionItem).filter(
                RecomendacionItem.id_recomendacion == recommendation_id,
                RecomendacionItem.id_variante == variant_id
            ).first()
            
            if item:
                item.fue_mostrado = True
                item.tiempo_visualizacion_segundos = view_duration_seconds
        
        self.db.commit()
    
    def track_product_click(self, 
                          session_id: str,
                          variant_id: int,
                          recommendation_id: Optional[int] = None,
                          click_position: Optional[int] = None) -> None:
        """Registrar cuando un producto es clicado"""
        
        # Registrar interacción de clic
        interaccion = InteraccionUsuario(
            id_sesion=session_id,
            tipo_interaccion="click",
            id_variante=variant_id,
            metadata_interaccion=json.dumps({
                "recommendation_id": recommendation_id,
                "click_position": click_position
            })
        )
        self.db.add(interaccion)
        
        # Si es parte de una recomendación, marcar como clicado
        if recommendation_id:
            item = self.db.query(RecomendacionItem).filter(
                RecomendacionItem.id_recomendacion == recommendation_id,
                RecomendacionItem.id_variante == variant_id
            ).first()
            
            if item:
                item.fue_clicado = True
                item.fecha_clic = datetime.utcnow()
        
        self.db.commit()
    
    def track_user_interaction(self, 
                              session_id: str,
                              interaction_type: str,
                              variant_id: Optional[int] = None,
                              metadata: Optional[Dict] = None,
                              duration_seconds: float = 0) -> None:
        """Registrar cualquier interacción del usuario"""
        
        interaccion = InteraccionUsuario(
            id_sesion=session_id,
            tipo_interaccion=interaction_type,
            id_variante=variant_id,
            metadata_interaccion=json.dumps(metadata) if metadata else None,
            duracion_segundos=duration_seconds
        )
        self.db.add(interaccion)
        self.db.commit()
    
    def calculate_session_metrics(self, session_id: str) -> Dict:
        """Calcular métricas para una sesión"""
        
        # Obtener datos de la sesión
        recomendaciones = self.db.query(RecomendacionSesion).filter(
            RecomendacionSesion.id_sesion == session_id
        ).all()
        
        interacciones = self.db.query(InteraccionUsuario).filter(
            InteraccionUsuario.id_sesion == session_id
        ).all()
        
        # Calcular métricas básicas
        total_recomendaciones = len(recomendaciones)
        total_productos_mostrados = 0
        total_clics = 0
        tiempo_total_visualizacion = 0
        
        productos_clicados = {}
        categorias_populares = {}
        
        # Procesar recomendaciones
        for rec in recomendaciones:
            items = self.db.query(RecomendacionItem).filter(
                RecomendacionItem.id_recomendacion == rec.id_recomendacion
            ).all()
            
            for item in items:
                if item.fue_mostrado:
                    total_productos_mostrados += 1
                    tiempo_total_visualizacion += item.tiempo_visualizacion_segundos or 0
                
                if item.fue_clicado:
                    total_clics += 1
                    
                    # Contar productos más clicados
                    producto_nombre = item.variante.producto.nombre
                    productos_clicados[producto_nombre] = productos_clicados.get(producto_nombre, 0) + 1
                    
                    # Contar categorías más populares
                    categoria_nombre = item.variante.producto.categoria.nombre
                    categorias_populares[categoria_nombre] = categorias_populares.get(categoria_nombre, 0) + 1
        
        # Calcular métricas derivadas
        tasa_clic = (total_clics / total_productos_mostrados) if total_productos_mostrados > 0 else 0
        tiempo_promedio_visualizacion = (tiempo_total_visualizacion / total_productos_mostrados) if total_productos_mostrados > 0 else 0
        
        # Top productos y categorías
        top_productos = sorted(productos_clicados.items(), key=lambda x: x[1], reverse=True)[:5]
        top_categorias = sorted(categorias_populares.items(), key=lambda x: x[1], reverse=True)[:5]
        
        # Crear registro de métricas
        metricas = MetricasSesion(
            id_sesion=session_id,
            total_recomendaciones_generadas=total_recomendaciones,
            total_productos_mostrados=total_productos_mostrados,
            total_clics=total_clics,
            tasa_clic=tasa_clic,
            tiempo_promedio_visualizacion=tiempo_promedio_visualizacion,
            productos_mas_clicados=json.dumps(top_productos),
            categorias_mas_populares=json.dumps(top_categorias)
        )
        
        self.db.add(metricas)
        self.db.commit()
        
        return {
            "total_recomendaciones": total_recomendaciones,
            "total_productos_mostrados": total_productos_mostrados,
            "total_clics": total_clics,
            "tasa_clic": tasa_clic,
            "tiempo_promedio_visualizacion": tiempo_promedio_visualizacion,
            "top_productos": top_productos,
            "top_categorias": top_categorias
        }
    
    def get_recommendation_performance(self, 
                                     days: int = 7,
                                     recommendation_type: Optional[str] = None) -> Dict:
        """Obtener métricas de rendimiento de recomendaciones"""
        
        from datetime import timedelta
        fecha_inicio = datetime.utcnow() - timedelta(days=days)
        
        query = self.db.query(RecomendacionSesion).filter(
            RecomendacionSesion.fecha_hora >= fecha_inicio
        )
        
        if recommendation_type:
            query = query.filter(RecomendacionSesion.tipo_recomendacion == recommendation_type)
        
        recomendaciones = query.all()
        
        # Calcular métricas agregadas
        total_recomendaciones = len(recomendaciones)
        total_productos_recomendados = sum(r.total_productos_recomendados for r in recomendaciones)
        tiempo_promedio_generacion = sum(r.tiempo_generacion_ms for r in recomendaciones) / total_recomendaciones if total_recomendaciones > 0 else 0
        
        # Calcular CTR promedio
        total_clics = 0
        total_mostrados = 0
        
        for rec in recomendaciones:
            items = self.db.query(RecomendacionItem).filter(
                RecomendacionItem.id_recomendacion == rec.id_recomendacion
            ).all()
            
            for item in items:
                if item.fue_mostrado:
                    total_mostrados += 1
                if item.fue_clicado:
                    total_clics += 1
        
        ctr_promedio = (total_clics / total_mostrados) if total_mostrados > 0 else 0
        
        return {
            "periodo_dias": days,
            "total_recomendaciones": total_recomendaciones,
            "total_productos_recomendados": total_productos_recomendados,
            "tiempo_promedio_generacion_ms": tiempo_promedio_generacion,
            "total_productos_mostrados": total_mostrados,
            "total_clics": total_clics,
            "ctr_promedio": ctr_promedio,
            "tipo_recomendacion": recommendation_type or "todos"
        }
    
    def get_top_performing_products(self, days: int = 7, limit: int = 10) -> List[Dict]:
        """Obtener productos con mejor rendimiento"""
        
        from datetime import timedelta
        fecha_inicio = datetime.utcnow() - timedelta(days=days)
        
        # Query para obtener productos más clicados
        query = self.db.query(ProductoVariante, InteraccionUsuario).join(
            InteraccionUsuario, InteraccionUsuario.id_variante == ProductoVariante.id_variante
        ).filter(
            InteraccionUsuario.tipo_interaccion == "click",
            InteraccionUsuario.fecha_hora >= fecha_inicio
        )
        
        # Contar clics por producto
        productos_clics = {}
        for variante, interaccion in query.all():
            producto_key = f"{variante.producto.nombre} - {variante.color} - {variante.talla}"
            if producto_key not in productos_clics:
                productos_clics[producto_key] = {
                    "producto": variante.producto.nombre,
                    "marca": variante.producto.marca,
                    "categoria": variante.producto.categoria.nombre,
                    "color": variante.color,
                    "talla": variante.talla,
                    "precio": variante.precio,
                    "clics": 0
                }
            productos_clics[producto_key]["clics"] += 1
        
        # Ordenar por clics y devolver top
        top_productos = sorted(productos_clics.values(), key=lambda x: x["clics"], reverse=True)
        return top_productos[:limit]

def get_recommendation_tracker(db: Session) -> RecommendationTracker:
    """Obtener instancia del tracker de recomendaciones"""
    return RecommendationTracker(db)




from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session
from database import database
from services.recommendation_tracker import get_recommendation_tracker
from typing import List, Dict, Optional
from datetime import datetime, timedelta

router = APIRouter(prefix="/analytics", tags=["Analytics"])

@router.get("/sesion/{session_id}/metricas")
def obtener_metricas_sesion(
    session_id: str,
    db: Session = Depends(database.get_db)
):
    """Obtener métricas completas de una sesión específica"""
    try:
        tracker = get_recommendation_tracker(db)
        metricas = tracker.calculate_session_metrics(session_id)
        
        return {
            "session_id": session_id,
            "metricas": metricas,
            "fecha_calculo": datetime.utcnow().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al calcular métricas: {str(e)}")

@router.get("/rendimiento")
def obtener_rendimiento_recomendaciones(
    dias: int = Query(7, ge=1, le=30, description="Días para analizar"),
    tipo_recomendacion: Optional[str] = Query(None, description="Tipo de recomendación específica"),
    db: Session = Depends(database.get_db)
):
    """Obtener métricas de rendimiento de recomendaciones"""
    try:
        tracker = get_recommendation_tracker(db)
        rendimiento = tracker.get_recommendation_performance(dias, tipo_recomendacion)
        
        return {
            "periodo_analisis": f"{dias} días",
            "tipo_recomendacion": tipo_recomendacion or "todos",
            "rendimiento": rendimiento,
            "fecha_analisis": datetime.utcnow().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al obtener rendimiento: {str(e)}")

@router.get("/productos-top")
def obtener_productos_top(
    dias: int = Query(7, ge=1, le=30, description="Días para analizar"),
    limite: int = Query(10, ge=1, le=50, description="Número de productos top"),
    db: Session = Depends(database.get_db)
):
    """Obtener productos con mejor rendimiento"""
    try:
        tracker = get_recommendation_tracker(db)
        top_productos = tracker.get_top_performing_products(dias, limite)
        
        return {
            "periodo_analisis": f"{dias} días",
            "total_productos": len(top_productos),
            "productos_top": top_productos,
            "fecha_analisis": datetime.utcnow().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al obtener productos top: {str(e)}")

@router.get("/dashboard")
def obtener_dashboard_analytics(
    dias: int = Query(7, ge=1, le=30, description="Días para el dashboard"),
    db: Session = Depends(database.get_db)
):
    """Obtener dashboard completo de analytics"""
    try:
        tracker = get_recommendation_tracker(db)
        
        # Obtener métricas generales
        rendimiento_general = tracker.get_recommendation_performance(dias)
        top_productos = tracker.get_top_performing_products(dias, 5)
        
        # Calcular métricas adicionales
        from database.models import RecomendacionSesion, InteraccionUsuario
        
        # Total de sesiones activas
        from sqlalchemy import func
        fecha_inicio = datetime.utcnow() - timedelta(days=dias)
        total_sesiones = db.query(func.count(func.distinct(RecomendacionSesion.id_sesion))).filter(
            RecomendacionSesion.fecha_hora >= fecha_inicio
        ).scalar()
        
        # Tipos de recomendación más usados
        tipos_recomendacion = db.query(
            RecomendacionSesion.tipo_recomendacion,
            func.count(RecomendacionSesion.id_recomendacion).label('count')
        ).filter(
            RecomendacionSesion.fecha_hora >= fecha_inicio
        ).group_by(RecomendacionSesion.tipo_recomendacion).all()
        
        # Algoritmos más efectivos (por CTR)
        algoritmos_ctr = {}
        for tipo_rec, count in tipos_recomendacion:
            rendimiento_tipo = tracker.get_recommendation_performance(dias, tipo_rec)
            algoritmos_ctr[tipo_rec] = {
                "total_recomendaciones": count,
                "ctr_promedio": rendimiento_tipo["ctr_promedio"]
            }
        
        return {
            "periodo_analisis": f"{dias} días",
            "resumen_general": {
                "total_sesiones_activas": total_sesiones,
                "total_recomendaciones": rendimiento_general["total_recomendaciones"],
                "total_productos_recomendados": rendimiento_general["total_productos_recomendados"],
                "ctr_promedio": rendimiento_general["ctr_promedio"],
                "tiempo_promedio_generacion_ms": rendimiento_general["tiempo_promedio_generacion_ms"]
            },
            "productos_top": top_productos,
            "tipos_recomendacion": [
                {"tipo": tipo, "total": count} for tipo, count in tipos_recomendacion
            ],
            "algoritmos_rendimiento": algoritmos_ctr,
            "fecha_analisis": datetime.utcnow().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al generar dashboard: {str(e)}")

@router.post("/track/view")
def trackear_vista_producto(
    session_id: str,
    variant_id: int,
    recommendation_id: Optional[int] = None,
    view_duration_seconds: float = Query(0, description="Duración de la vista en segundos"),
    db: Session = Depends(database.get_db)
):
    """Registrar vista de un producto"""
    try:
        tracker = get_recommendation_tracker(db)
        tracker.track_product_view(session_id, variant_id, recommendation_id, view_duration_seconds)
        
        return {
            "message": "Vista registrada exitosamente",
            "session_id": session_id,
            "variant_id": variant_id,
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al registrar vista: {str(e)}")

@router.post("/track/click")
def trackear_clic_producto(
    session_id: str,
    variant_id: int,
    recommendation_id: Optional[int] = None,
    click_position: Optional[int] = None,
    db: Session = Depends(database.get_db)
):
    """Registrar clic en un producto"""
    try:
        tracker = get_recommendation_tracker(db)
        tracker.track_product_click(session_id, variant_id, recommendation_id, click_position)
        
        return {
            "message": "Clic registrado exitosamente",
            "session_id": session_id,
            "variant_id": variant_id,
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al registrar clic: {str(e)}")

@router.post("/track/interaction")
def trackear_interaccion(
    session_id: str,
    interaction_type: str,
    variant_id: Optional[int] = None,
    metadata: Optional[Dict] = None,
    duration_seconds: float = Query(0, description="Duración de la interacción"),
    db: Session = Depends(database.get_db)
):
    """Registrar cualquier interacción del usuario"""
    try:
        tracker = get_recommendation_tracker(db)
        tracker.track_user_interaction(session_id, interaction_type, variant_id, metadata, duration_seconds)
        
        return {
            "message": "Interacción registrada exitosamente",
            "session_id": session_id,
            "interaction_type": interaction_type,
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al registrar interacción: {str(e)}")

@router.get("/export/{session_id}")
def exportar_datos_sesion(
    session_id: str,
    formato: str = Query("json", description="Formato de exportación: json, csv"),
    db: Session = Depends(database.get_db)
):
    """Exportar todos los datos de una sesión"""
    try:
        tracker = get_recommendation_tracker(db)
        
        # Obtener métricas de la sesión
        metricas = tracker.calculate_session_metrics(session_id)
        
        # Obtener datos detallados
        from database.models import RecomendacionSesion, RecomendacionItem, InteraccionUsuario
        
        recomendaciones = db.query(RecomendacionSesion).filter(
            RecomendacionSesion.id_sesion == session_id
        ).all()
        
        interacciones = db.query(InteraccionUsuario).filter(
            InteraccionUsuario.id_sesion == session_id
        ).all()
        
        datos_export = {
            "session_id": session_id,
            "fecha_exportacion": datetime.utcnow().isoformat(),
            "metricas": metricas,
            "recomendaciones": [
                {
                    "id": r.id_recomendacion,
                    "tipo": r.tipo_recomendacion,
                    "algoritmo": r.algoritmo_usado,
                    "filtros": r.filtros_aplicados,
                    "total_productos": r.total_productos_recomendados,
                    "tiempo_generacion_ms": r.tiempo_generacion_ms,
                    "fecha": r.fecha_hora.isoformat()
                }
                for r in recomendaciones
            ],
            "interacciones": [
                {
                    "tipo": i.tipo_interaccion,
                    "variant_id": i.id_variante,
                    "metadata": i.metadata_interaccion,
                    "duracion_segundos": i.duracion_segundos,
                    "fecha": i.fecha_hora.isoformat()
                }
                for i in interacciones
            ]
        }
        
        if formato.lower() == "csv":
            # Convertir a CSV (implementación básica)
            import csv
            import io
            
            output = io.StringIO()
            writer = csv.writer(output)
            
            # Escribir métricas
            writer.writerow(["Metrica", "Valor"])
            for key, value in metricas.items():
                writer.writerow([key, value])
            
            return {
                "message": "Datos exportados en formato CSV",
                "data": output.getvalue(),
                "content_type": "text/csv"
            }
        else:
            return datos_export
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al exportar datos: {str(e)}")



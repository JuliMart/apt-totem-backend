"""
Script para probar el sistema de tracking de recomendaciones
"""
import requests
import json
import uuid
from database.database import SessionLocal
from services.recommendation_tracker import get_recommendation_tracker

def test_tracking_system():
    """Probar el sistema de tracking completo"""
    print("📊 Probando sistema de tracking de recomendaciones...")
    
    base_url = "http://127.0.0.1:8000"
    
    # Crear una sesión de prueba
    session_id = str(uuid.uuid4())
    print(f"🆔 Sesión de prueba: {session_id}")
    
    # Probar recomendaciones con tracking
    print("\n🎯 Generando recomendaciones con tracking...")
    
    # Recomendación por categoría
    print("  📂 Recomendación por categoría (Zapatillas)")
    response = requests.get(f"{base_url}/recomendaciones/categoria/Zapatillas?limit=3&session_id={session_id}")
    if response.status_code == 200:
        productos = response.json()
        print(f"    ✅ {len(productos)} productos recomendados")
        
        # Simular vistas y clics
        for i, producto in enumerate(productos):
            print(f"    👁️ Vista producto {i+1}: {producto['producto']}")
            
            # Trackear vista
            view_response = requests.post(f"{base_url}/analytics/track/view", params={
                "session_id": session_id,
                "variant_id": producto['id_variante'],
                "view_duration_seconds": 2.5
            })
            
            if i == 0:  # Simular clic en el primer producto
                print(f"    🖱️ Clic en producto: {producto['producto']}")
                click_response = requests.post(f"{base_url}/analytics/track/click", params={
                    "session_id": session_id,
                    "variant_id": producto['id_variante'],
                    "click_position": i + 1
                })
    
    # Recomendación por marca
    print("\n  🏷️ Recomendación por marca (Nike)")
    response = requests.get(f"{base_url}/recomendaciones/marca/Nike?limit=2&session_id={session_id}")
    if response.status_code == 200:
        productos = response.json()
        print(f"    ✅ {len(productos)} productos recomendados")
        
        # Simular interacciones
        for producto in productos:
            requests.post(f"{base_url}/analytics/track/view", params={
                "session_id": session_id,
                "variant_id": producto['id_variante'],
                "view_duration_seconds": 1.8
            })
    
    # Recomendación personalizada
    print("\n  👤 Recomendación personalizada (joven)")
    response = requests.get(f"{base_url}/recomendaciones/personalizadas?edad=18-25&limit=3&session_id={session_id}")
    if response.status_code == 200:
        productos = response.json()
        print(f"    ✅ {len(productos)} productos recomendados")
        
        # Simular más interacciones
        for i, producto in enumerate(productos):
            requests.post(f"{base_url}/analytics/track/view", params={
                "session_id": session_id,
                "variant_id": producto['id_variante'],
                "view_duration_seconds": 3.2
            })
            
            if i < 2:  # Clic en los primeros 2 productos
                requests.post(f"{base_url}/analytics/track/click", params={
                    "session_id": session_id,
                    "variant_id": producto['id_variante'],
                    "click_position": i + 1
                })
    
    # Obtener métricas de la sesión
    print(f"\n📈 Obteniendo métricas de la sesión...")
    response = requests.get(f"{base_url}/analytics/sesion/{session_id}/metricas")
    if response.status_code == 200:
        metricas = response.json()
        print("  📊 Métricas de la sesión:")
        for key, value in metricas['metricas'].items():
            if isinstance(value, float):
                print(f"    {key}: {value:.2f}")
            else:
                print(f"    {key}: {value}")
    
    # Obtener dashboard de analytics
    print(f"\n📊 Obteniendo dashboard de analytics...")
    response = requests.get(f"{base_url}/analytics/dashboard?dias=1")
    if response.status_code == 200:
        dashboard = response.json()
        print("  📈 Dashboard Analytics:")
        print(f"    Total sesiones activas: {dashboard['resumen_general']['total_sesiones_activas']}")
        print(f"    Total recomendaciones: {dashboard['resumen_general']['total_recomendaciones']}")
        print(f"    CTR promedio: {dashboard['resumen_general']['ctr_promedio']:.2%}")
        print(f"    Tiempo promedio generación: {dashboard['resumen_general']['tiempo_promedio_generacion_ms']:.0f}ms")
        
        print("\n  🏆 Productos top:")
        for i, producto in enumerate(dashboard['productos_top'][:3], 1):
            print(f"    {i}. {producto['producto']} ({producto['marca']}) - {producto['clics']} clics")
    
    # Obtener rendimiento de recomendaciones
    print(f"\n⚡ Obteniendo rendimiento de recomendaciones...")
    response = requests.get(f"{base_url}/analytics/rendimiento?dias=1")
    if response.status_code == 200:
        rendimiento = response.json()
        print("  📊 Rendimiento:")
        print(f"    Total recomendaciones: {rendimiento['rendimiento']['total_recomendaciones']}")
        print(f"    Total productos mostrados: {rendimiento['rendimiento']['total_productos_mostrados']}")
        print(f"    Total clics: {rendimiento['rendimiento']['total_clics']}")
        print(f"    CTR promedio: {rendimiento['rendimiento']['ctr_promedio']:.2%}")
    
    print(f"\n🎉 ¡Sistema de tracking probado exitosamente!")
    print(f"📝 Sesión de prueba: {session_id}")
    print("📊 Puedes ver más detalles en: http://127.0.0.1:8000/docs")

def test_database_tracking():
    """Probar tracking directamente desde la base de datos"""
    print("\n🗄️ Probando tracking desde base de datos...")
    
    db = SessionLocal()
    try:
        tracker = get_recommendation_tracker(db)
        
        # Crear una sesión de prueba
        session_id = str(uuid.uuid4())
        
        # Simular generación de recomendación
        productos_ejemplo = [
            {"id_variante": 1, "score": 0.95},
            {"id_variante": 2, "score": 0.87},
            {"id_variante": 3, "score": 0.82}
        ]
        
        recommendation_id = tracker.track_recommendation_generation(
            session_id=session_id,
            recommendation_type="test",
            filters_applied={"test": True},
            algorithm_used="test_algorithm",
            recommended_products=productos_ejemplo,
            generation_time_ms=150
        )
        
        print(f"  ✅ Recomendación registrada con ID: {recommendation_id}")
        
        # Simular vistas y clics
        tracker.track_product_view(session_id, 1, recommendation_id, 2.5)
        tracker.track_product_click(session_id, 1, recommendation_id, 1)
        
        tracker.track_product_view(session_id, 2, recommendation_id, 1.8)
        
        print("  ✅ Interacciones registradas")
        
        # Calcular métricas
        metricas = tracker.calculate_session_metrics(session_id)
        print("  📊 Métricas calculadas:")
        print(f"    Total recomendaciones: {metricas['total_recomendaciones']}")
        print(f"    Total productos mostrados: {metricas['total_productos_mostrados']}")
        print(f"    Total clics: {metricas['total_clics']}")
        print(f"    Tasa de clic: {metricas['tasa_clic']:.2%}")
        
    except Exception as e:
        print(f"  ❌ Error: {e}")
    finally:
        db.close()

def main():
    """Función principal"""
    print("📊 Sistema de Tracking de Recomendaciones - Pruebas Completas")
    print("=" * 70)
    
    # Probar sistema completo via API
    test_tracking_system()
    
    # Probar directamente desde base de datos
    test_database_tracking()
    
    print("\n🎯 Endpoints de Analytics disponibles:")
    print("  • GET /analytics/sesion/{session_id}/metricas - Métricas de sesión")
    print("  • GET /analytics/rendimiento - Rendimiento de recomendaciones")
    print("  • GET /analytics/productos-top - Productos con mejor rendimiento")
    print("  • GET /analytics/dashboard - Dashboard completo")
    print("  • POST /analytics/track/view - Registrar vista de producto")
    print("  • POST /analytics/track/click - Registrar clic en producto")
    print("  • POST /analytics/track/interaction - Registrar interacción")
    print("  • GET /analytics/export/{session_id} - Exportar datos de sesión")

if __name__ == "__main__":
    main()





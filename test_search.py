"""
Script para probar el sistema de búsqueda y recomendaciones
"""
import requests
import json
import uuid
from database.database import SessionLocal
from services.search_engine import get_search_recommendation_engine

def test_search_system():
    """Probar el sistema de búsqueda completo"""
    print("🔍 Probando sistema de búsqueda y recomendaciones...")
    
    base_url = "http://127.0.0.1:8000"
    
    # Crear una sesión de prueba
    session_id = str(uuid.uuid4())
    print(f"🆔 Sesión de prueba: {session_id}")
    
    # Lista de búsquedas para probar
    test_queries = [
        "zapatillas",
        "nike",
        "azul",
        "chaquetas",
        "adidas",
        "rojo",
        "pantalones",
        "converse",
        "poleras",
        "accesorios"
    ]
    
    print("\n🔍 Probando búsquedas básicas...")
    for query in test_queries[:5]:  # Probar las primeras 5
        print(f"\n  🔎 Búsqueda: '{query}'")
        
        try:
            response = requests.get(f"{base_url}/busqueda/?q={query}&limit=5&session_id={session_id}")
            
            if response.status_code == 200:
                data = response.json()
                resultados = data['results']
                
                print(f"    ✅ {len(resultados)} resultados encontrados")
                
                # Mostrar primeros resultados
                for i, producto in enumerate(resultados[:3], 1):
                    score = producto.get('search_score', 0)
                    print(f"      {i}. {producto['producto']} ({producto['marca']}) - Score: {score:.2f}")
                
                # Simular interacciones
                if resultados:
                    # Simular vista del primer resultado
                    requests.post(f"{base_url}/analytics/track/view", params={
                        "session_id": session_id,
                        "variant_id": resultados[0]['id_variante'],
                        "view_duration_seconds": 2.0
                    })
                    
                    # Simular clic en el primer resultado
                    requests.post(f"{base_url}/analytics/track/click", params={
                        "session_id": session_id,
                        "variant_id": resultados[0]['id_variante'],
                        "click_position": 1
                    })
                    
                    print(f"    👁️ Interacciones simuladas para '{resultados[0]['producto']}'")
            else:
                print(f"    ❌ Error {response.status_code}: {response.text}")
                
        except requests.RequestException as e:
            print(f"    ❌ Error de conexión: {e}")
    
    # Probar sugerencias de búsqueda
    print(f"\n💡 Probando sugerencias de búsqueda...")
    test_suggestions = ["zap", "nik", "az", "cha", "ad"]
    
    for query in test_suggestions:
        try:
            response = requests.get(f"{base_url}/busqueda/sugerencias?q={query}&limit=3")
            
            if response.status_code == 200:
                data = response.json()
                sugerencias = data['suggestions']
                
                print(f"  🔍 '{query}' → {sugerencias}")
            else:
                print(f"  ❌ Error en sugerencias para '{query}': {response.status_code}")
                
        except requests.RequestException as e:
            print(f"  ❌ Error de conexión: {e}")
    
    # Probar autocompletar
    print(f"\n⚡ Probando autocompletar...")
    for query in test_suggestions:
        try:
            response = requests.get(f"{base_url}/busqueda/autocomplete?q={query}&limit=3")
            
            if response.status_code == 200:
                data = response.json()
                sugerencias = data['suggestions']
                
                print(f"  🔍 '{query}' → {len(sugerencias)} sugerencias")
                for sug in sugerencias:
                    print(f"    - {sug['text']} ({sug['product_count']} productos)")
            else:
                print(f"  ❌ Error en autocompletar para '{query}': {response.status_code}")
                
        except requests.RequestException as e:
            print(f"  ❌ Error de conexión: {e}")
    
    # Probar analytics de búsqueda
    print(f"\n📊 Probando analytics de búsqueda...")
    for query in ["zapatillas", "nike", "azul"]:
        try:
            response = requests.get(f"{base_url}/busqueda/analytics?q={query}")
            
            if response.status_code == 200:
                analytics = response.json()
                
                print(f"  📈 Analytics para '{query}':")
                print(f"    Total resultados: {analytics['total_results']}")
                print(f"    Calidad búsqueda: {analytics['search_quality']}")
                print(f"    Categorías: {analytics['categories_found']}")
                print(f"    Marcas: {analytics['brands_found']}")
                print(f"    Rango precio: ${analytics['price_range']['min']:,.0f} - ${analytics['price_range']['max']:,.0f}")
            else:
                print(f"  ❌ Error en analytics para '{query}': {response.status_code}")
                
        except requests.RequestException as e:
            print(f"  ❌ Error de conexión: {e}")
    
    # Probar búsquedas populares
    print(f"\n🔥 Probando búsquedas populares...")
    try:
        response = requests.get(f"{base_url}/busqueda/popular?limit=5")
        
        if response.status_code == 200:
            data = response.json()
            populares = data['popular_searches']
            
            print("  🏆 Búsquedas populares:")
            for i, busqueda in enumerate(populares, 1):
                print(f"    {i}. '{busqueda['query']}' ({busqueda['count']} búsquedas) - {busqueda['category']}")
        else:
            print(f"  ❌ Error en búsquedas populares: {response.status_code}")
            
    except requests.RequestException as e:
        print(f"  ❌ Error de conexión: {e}")
    
    # Probar tendencias
    print(f"\n📈 Probando tendencias de búsqueda...")
    try:
        response = requests.get(f"{base_url}/busqueda/trending?limit=5")
        
        if response.status_code == 200:
            data = response.json()
            tendencias = data['trending_searches']
            
            print("  📊 Tendencias actuales:")
            for i, tendencia in enumerate(tendencias, 1):
                emoji = "📈" if tendencia['trend'] == "up" else "📉" if tendencia['trend'] == "down" else "➡️"
                print(f"    {i}. '{tendencia['query']}' {emoji} {tendencia['change']}")
        else:
            print(f"  ❌ Error en tendencias: {response.status_code}")
            
    except requests.RequestException as e:
        print(f"  ❌ Error de conexión: {e}")
    
    # Probar filtros disponibles
    print(f"\n🔧 Probando filtros disponibles...")
    try:
        response = requests.get(f"{base_url}/busqueda/filters?q=zapatillas")
        
        if response.status_code == 200:
            data = response.json()
            filtros = data['filters']
            
            print("  🎛️ Filtros para 'zapatillas':")
            print(f"    Categorías: {len(filtros['categories'])} disponibles")
            print(f"    Marcas: {len(filtros['brands'])} disponibles")
            print(f"    Colores: {len(filtros['colors'])} disponibles")
            print(f"    Rango precio: ${filtros['price_range']['min']:,.0f} - ${filtros['price_range']['max']:,.0f}")
        else:
            print(f"  ❌ Error en filtros: {response.status_code}")
            
    except requests.RequestException as e:
        print(f"  ❌ Error de conexión: {e}")
    
    # Verificar salud del sistema
    print(f"\n🏥 Verificando salud del sistema de búsqueda...")
    try:
        response = requests.get(f"{base_url}/busqueda/health")
        
        if response.status_code == 200:
            health = response.json()
            print(f"  ✅ Estado: {health['status']}")
            print(f"  📊 Productos: {health['database_stats']['total_productos']}")
            print(f"  📊 Variantes: {health['database_stats']['total_variantes']}")
            print(f"  📊 Categorías: {health['database_stats']['total_categorias']}")
        else:
            print(f"  ❌ Error en health check: {response.status_code}")
            
    except requests.RequestException as e:
        print(f"  ❌ Error de conexión: {e}")
    
    print(f"\n🎉 ¡Sistema de búsqueda probado exitosamente!")
    print(f"📝 Sesión de prueba: {session_id}")

def test_database_search():
    """Probar búsqueda directamente desde la base de datos"""
    print("\n🗄️ Probando búsqueda desde base de datos...")
    
    db = SessionLocal()
    try:
        search_engine = get_search_recommendation_engine(db)
        
        # Probar diferentes tipos de búsqueda
        test_queries = ["nike", "zapatillas", "azul", "chaquetas", "adidas"]
        
        for query in test_queries:
            print(f"\n  🔍 Búsqueda: '{query}'")
            
            # Buscar productos
            productos = search_engine.search_products(query, limit=3)
            
            print(f"    ✅ {len(productos)} productos encontrados")
            
            for i, producto in enumerate(productos, 1):
                score = producto.get('search_score', 0)
                print(f"      {i}. {producto['producto']} ({producto['marca']}) - Score: {score:.2f}")
            
            # Obtener sugerencias
            sugerencias = search_engine.get_search_suggestions(query, limit=3)
            print(f"    💡 Sugerencias: {sugerencias}")
            
            # Obtener analytics
            analytics = search_engine.get_search_analytics(query)
            print(f"    📊 Analytics: {analytics['total_results']} resultados, calidad: {analytics['search_quality']}")
        
    except Exception as e:
        print(f"  ❌ Error: {e}")
    finally:
        db.close()

def main():
    """Función principal"""
    print("🔍 Sistema de Búsqueda y Recomendaciones - Pruebas Completas")
    print("=" * 70)
    
    # Probar sistema completo via API
    test_search_system()
    
    # Probar directamente desde base de datos
    test_database_search()
    
    print("\n🎯 Endpoints de Búsqueda disponibles:")
    print("  • GET /busqueda/?q={query} - Búsqueda principal")
    print("  • GET /busqueda/sugerencias?q={query} - Sugerencias de búsqueda")
    print("  • GET /busqueda/autocomplete?q={query} - Autocompletar")
    print("  • GET /busqueda/analytics?q={query} - Analytics de búsqueda")
    print("  • GET /busqueda/popular - Búsquedas populares")
    print("  • GET /busqueda/trending - Tendencias de búsqueda")
    print("  • GET /busqueda/filters?q={query} - Filtros disponibles")
    print("  • GET /busqueda/health - Estado del sistema")

if __name__ == "__main__":
    main()


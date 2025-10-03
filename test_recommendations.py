"""
Script para probar el sistema de recomendaciones
"""
import requests
import json
from database.database import SessionLocal
from services.recommendation_engine import get_recommendation_engine

def test_recommendations():
    """Probar el sistema de recomendaciones"""
    print("🎯 Probando sistema de recomendaciones...")
    
    base_url = "http://127.0.0.1:8000"
    
    # Pruebas de endpoints
    tests = [
        {
            "name": "Recomendaciones por categoría (Zapatillas)",
            "url": f"{base_url}/recomendaciones/categoria/Zapatillas?limit=5"
        },
        {
            "name": "Recomendaciones por marca (Nike)",
            "url": f"{base_url}/recomendaciones/marca/Nike?limit=5"
        },
        {
            "name": "Recomendaciones por color (Azul)",
            "url": f"{base_url}/recomendaciones/color/Azul?limit=5"
        },
        {
            "name": "Recomendaciones por presupuesto ($50,000)",
            "url": f"{base_url}/recomendaciones/presupuesto?presupuesto_max=50000&limit=5"
        },
        {
            "name": "Recomendaciones personalizadas (joven)",
            "url": f"{base_url}/recomendaciones/personalizadas?edad=18-25&limit=5"
        },
        {
            "name": "Recomendaciones estacionales (verano)",
            "url": f"{base_url}/recomendaciones/estacionales?temporada=verano&limit=5"
        },
        {
            "name": "Productos trending",
            "url": f"{base_url}/recomendaciones/trending?limit=5"
        }
    ]
    
    for test in tests:
        try:
            print(f"\n🧪 {test['name']}")
            response = requests.get(test['url'], timeout=5)
            
            if response.status_code == 200:
                data = response.json()
                print(f"  ✅ {len(data)} productos encontrados")
                
                # Mostrar primeros productos
                for i, product in enumerate(data[:3], 1):
                    print(f"    {i}. {product['producto']} ({product['marca']}) - ${product['precio']:,}")
            else:
                print(f"  ❌ Error {response.status_code}: {response.text}")
                
        except requests.RequestException as e:
            print(f"  ❌ Error de conexión: {e}")

def test_similar_products():
    """Probar recomendaciones de productos similares"""
    print("\n🔗 Probando productos similares...")
    
    base_url = "http://127.0.0.1:8000"
    
    # Obtener un producto para probar
    try:
        response = requests.get(f"{base_url}/productos/", timeout=5)
        if response.status_code == 200:
            products = response.json()
            if products:
                first_product_id = products[0]['id_producto']
                
                # Probar productos similares
                similar_url = f"{base_url}/recomendaciones/similar/{first_product_id}?limit=3"
                similar_response = requests.get(similar_url, timeout=5)
                
                if similar_response.status_code == 200:
                    similar_products = similar_response.json()
                    print(f"  ✅ {len(similar_products)} productos similares encontrados")
                    
                    for i, product in enumerate(similar_products, 1):
                        print(f"    {i}. {product['producto']} ({product['marca']}) - ${product['precio']:,}")
                else:
                    print(f"  ❌ Error al obtener productos similares: {similar_response.status_code}")
                    
    except requests.RequestException as e:
        print(f"  ❌ Error: {e}")

def test_cross_sell():
    """Probar recomendaciones cross-sell"""
    print("\n🛒 Probando productos complementarios...")
    
    base_url = "http://127.0.0.1:8000"
    
    try:
        # Obtener un producto para probar
        response = requests.get(f"{base_url}/productos/", timeout=5)
        if response.status_code == 200:
            products = response.json()
            if products:
                first_product_id = products[0]['id_producto']
                
                # Probar productos complementarios
                cross_sell_url = f"{base_url}/recomendaciones/cross-sell/{first_product_id}?limit=3"
                cross_sell_response = requests.get(cross_sell_url, timeout=5)
                
                if cross_sell_response.status_code == 200:
                    cross_sell_products = cross_sell_response.json()
                    print(f"  ✅ {len(cross_sell_products)} productos complementarios encontrados")
                    
                    for i, product in enumerate(cross_sell_products, 1):
                        print(f"    {i}. {product['producto']} ({product['marca']}) - ${product['precio']:,}")
                else:
                    print(f"  ❌ Error al obtener productos complementarios: {cross_sell_response.status_code}")
                    
    except requests.RequestException as e:
        print(f"  ❌ Error: {e}")

def test_database_recommendations():
    """Probar recomendaciones directamente desde la base de datos"""
    print("\n🗄️ Probando recomendaciones desde base de datos...")
    
    db = SessionLocal()
    try:
        engine = get_recommendation_engine(db)
        
        # Probar diferentes tipos de recomendaciones
        print("  📊 Recomendaciones por categoría (Zapatillas):")
        zapatillas = engine.get_products_by_category("Zapatillas", 3)
        for i, product in enumerate(zapatillas, 1):
            print(f"    {i}. {product['producto']} ({product['marca']}) - ${product['precio']:,}")
        
        print("\n  🎨 Recomendaciones por color (Rojo):")
        rojos = engine.get_products_by_color("Rojo", 3)
        for i, product in enumerate(rojos, 1):
            print(f"    {i}. {product['producto']} ({product['marca']}) - ${product['precio']:,}")
        
        print("\n  💰 Recomendaciones por presupuesto ($40,000):")
        presupuesto = engine.get_budget_recommendations(40000, 3)
        for i, product in enumerate(presupuesto, 1):
            print(f"    {i}. {product['producto']} ({product['marca']}) - ${product['precio']:,}")
        
        print("\n  👤 Recomendaciones personalizadas (joven):")
        personalizadas = engine.get_personalized_recommendations(age_range="18-25", limit=3)
        for i, product in enumerate(personalizadas, 1):
            print(f"    {i}. {product['producto']} ({product['marca']}) - ${product['precio']:,}")
        
    except Exception as e:
        print(f"  ❌ Error: {e}")
    finally:
        db.close()

def main():
    """Función principal"""
    print("🎯 Sistema de Recomendaciones - Pruebas Completas")
    print("=" * 60)
    
    # Probar endpoints de la API
    test_recommendations()
    
    # Probar productos similares
    test_similar_products()
    
    # Probar cross-sell
    test_cross_sell()
    
    # Probar directamente desde base de datos
    test_database_recommendations()
    
    print("\n🎉 ¡Pruebas completadas!")
    print("\n📝 Endpoints disponibles:")
    print("  • GET /recomendaciones/ - Recomendaciones básicas")
    print("  • GET /recomendaciones/categoria/{categoria} - Por categoría")
    print("  • GET /recomendaciones/marca/{marca} - Por marca")
    print("  • GET /recomendaciones/color/{color} - Por color")
    print("  • GET /recomendaciones/presupuesto - Por presupuesto")
    print("  • GET /recomendaciones/personalizadas - Personalizadas")
    print("  • GET /recomendaciones/similar/{id} - Productos similares")
    print("  • GET /recomendaciones/cross-sell/{id} - Productos complementarios")
    print("  • GET /recomendaciones/trending - Productos trending")
    print("  • GET /recomendaciones/estacionales - Estacionales")

if __name__ == "__main__":
    main()





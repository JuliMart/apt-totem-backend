"""
Script de ejemplo para probar la funcionalidad de retail API
"""
import requests
import json
from database.database import SessionLocal
from database.models import Categoria, Producto, ProductoVariante
from services.retail_api import get_retail_api_client

def test_local_database():
    """Probar la base de datos local"""
    print("🗄️ Probando base de datos local...")
    
    db = SessionLocal()
    try:
        # Contar registros existentes
        categories_count = db.query(Categoria).count()
        products_count = db.query(Producto).count()
        variants_count = db.query(ProductoVariante).count()
        
        print(f"  📊 Categorías: {categories_count}")
        print(f"  📊 Productos: {products_count}")
        print(f"  📊 Variantes: {variants_count}")
        
        # Mostrar algunas categorías
        categories = db.query(Categoria).limit(5).all()
        print(f"  📋 Primeras categorías: {[c.nombre for c in categories]}")
        
        # Mostrar algunos productos
        products = db.query(Producto).limit(3).all()
        for p in products:
            print(f"  🛍️ {p.nombre} ({p.marca})")
        
        return True
        
    except Exception as e:
        print(f"  ❌ Error: {e}")
        return False
    finally:
        db.close()

def test_external_api():
    """Probar la API externa"""
    print("\n🌐 Probando API externa (Fake Store API)...")
    
    try:
        client = get_retail_api_client()
        
        # Probar health check
        health = client.service.get_categories()
        print(f"  ✅ API conectada - {len(health)} categorías disponibles")
        
        # Obtener categorías
        categories = client.service.get_categories()
        print(f"  📋 Categorías: {categories}")
        
        # Obtener algunos productos
        products = client.service.get_products(5)
        print(f"  🛍️ Primeros productos:")
        for p in products[:3]:
            print(f"    - {p['title']} (${p['price']})")
        
        # Probar búsqueda
        search_results = client.service.search_products("shirt")
        print(f"  🔍 Búsqueda 'shirt': {len(search_results)} resultados")
        
        return True
        
    except Exception as e:
        print(f"  ❌ Error: {e}")
        return False

def test_api_endpoints():
    """Probar los endpoints de la API"""
    print("\n🔌 Probando endpoints de la API...")
    
    base_url = "http://localhost:8000"
    
    endpoints_to_test = [
        "/",
        "/retail-api/health",
        "/retail-api/categories",
        "/retail-api/products?limit=5",
        "/retail-api/search?q=shirt"
    ]
    
    for endpoint in endpoints_to_test:
        try:
            response = requests.get(f"{base_url}{endpoint}", timeout=5)
            if response.status_code == 200:
                data = response.json()
                print(f"  ✅ {endpoint} - OK")
                if endpoint == "/retail-api/categories":
                    print(f"    📋 {len(data.get('categories', []))} categorías")
                elif endpoint == "/retail-api/products":
                    print(f"    🛍️ {len(data.get('products', []))} productos")
            else:
                print(f"  ⚠️ {endpoint} - Status {response.status_code}")
        except requests.RequestException as e:
            print(f"  ❌ {endpoint} - Error: {e}")

def sync_external_data():
    """Sincronizar datos externos"""
    print("\n🔄 Sincronizando datos externos...")
    
    try:
        db = SessionLocal()
        client = get_retail_api_client()
        
        # Sincronizar categorías
        categories_synced = client.service.sync_categories_to_db(db)
        print(f"  ✅ {categories_synced} categorías sincronizadas")
        
        # Sincronizar productos
        products_synced = client.service.sync_products_to_db(db, 10)
        print(f"  ✅ {products_synced} productos sincronizados")
        
        # Mostrar estadísticas finales
        categories_count = db.query(Categoria).count()
        products_count = db.query(Producto).count()
        variants_count = db.query(ProductoVariante).count()
        
        print(f"  📊 Total categorías: {categories_count}")
        print(f"  📊 Total productos: {products_count}")
        print(f"  📊 Total variantes: {variants_count}")
        
        return True
        
    except Exception as e:
        print(f"  ❌ Error: {e}")
        return False
    finally:
        db.close()

def main():
    """Función principal"""
    print("🛍️ Probando funcionalidad de Retail API")
    print("=" * 50)
    
    # Probar base de datos local
    local_ok = test_local_database()
    
    # Probar API externa
    external_ok = test_external_api()
    
    # Probar endpoints (solo si el servidor está corriendo)
    print("\n💡 Para probar endpoints, ejecuta primero: uvicorn api.main:app --reload")
    # test_api_endpoints()
    
    # Sincronizar datos si ambas APIs funcionan
    if local_ok and external_ok:
        sync_ok = sync_external_data()
        
        if sync_ok:
            print("\n🎉 ¡Todas las pruebas pasaron exitosamente!")
            print("\n📝 Próximos pasos:")
            print("  1. Ejecuta: python populate_database.py")
            print("  2. Ejecuta: uvicorn api.main:app --reload")
            print("  3. Visita: http://localhost:8000/docs")
            print("  4. Prueba los endpoints de /retail-api/")
        else:
            print("\n⚠️ Hubo problemas con la sincronización")
    else:
        print("\n❌ Algunas pruebas fallaron")

if __name__ == "__main__":
    main()


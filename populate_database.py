"""
Script para poblar la base de datos con datos de retail de ejemplo
"""
import random
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from database.database import engine, SessionLocal
from database.models import (
    Categoria, Producto, ProductoVariante, Sesion, 
    ConsultaVoz, Deteccion
)

def get_db():
    """Obtener sesión de base de datos"""
    db = SessionLocal()
    try:
        return db
    finally:
        pass

def populate_categories(db: Session):
    """Poblar categorías de ropa"""
    categories = [
        "Zapatillas",
        "Poleras",
        "Chaquetas", 
        "Pantalones",
        "Vestidos",
        "Accesorios",
        "Gorros",
        "Gafas",
        "Relojes",
        "Bolsos"
    ]
    
    for cat_name in categories:
        existing = db.query(Categoria).filter(Categoria.nombre == cat_name).first()
        if not existing:
            categoria = Categoria(nombre=cat_name)
            db.add(categoria)
    
    db.commit()
    print(f"✅ Creadas {len(categories)} categorías")

def populate_products(db: Session):
    """Poblar productos con variantes"""
    
    # Datos de productos por categoría
    products_data = {
        "Zapatillas": [
            {"nombre": "Nike Air Max 270", "marca": "Nike", "precio_base": 89990},
            {"nombre": "Adidas Ultraboost 22", "marca": "Adidas", "precio_base": 99990},
            {"nombre": "Converse Chuck Taylor", "marca": "Converse", "precio_base": 59990},
            {"nombre": "Vans Old Skool", "marca": "Vans", "precio_base": 69990},
            {"nombre": "Puma RS-X", "marca": "Puma", "precio_base": 79990}
        ],
        "Poleras": [
            {"nombre": "Polo Ralph Lauren", "marca": "Ralph Lauren", "precio_base": 39990},
            {"nombre": "Camiseta Nike Dri-FIT", "marca": "Nike", "precio_base": 29990},
            {"nombre": "Hoodie Adidas Originals", "marca": "Adidas", "precio_base": 59990},
            {"nombre": "Sweater Tommy Hilfiger", "marca": "Tommy Hilfiger", "precio_base": 49990},
            {"nombre": "Camisa Lacoste", "marca": "Lacoste", "precio_base": 69990}
        ],
        "Chaquetas": [
            {"nombre": "Chaqueta North Face", "marca": "The North Face", "precio_base": 129990},
            {"nombre": "Blazer Hugo Boss", "marca": "Hugo Boss", "precio_base": 149990},
            {"nombre": "Chaqueta Columbia", "marca": "Columbia", "precio_base": 99990},
            {"nombre": "Saco Zara", "marca": "Zara", "precio_base": 49990},
            {"nombre": "Chaqueta Patagonia", "marca": "Patagonia", "precio_base": 119990}
        ],
        "Pantalones": [
            {"nombre": "Jeans Levis 501", "marca": "Levi's", "precio_base": 79990},
            {"nombre": "Pantalón Nike Tech Fleece", "marca": "Nike", "precio_base": 59990},
            {"nombre": "Chino Dockers", "marca": "Dockers", "precio_base": 49990},
            {"nombre": "Pantalón Adidas Tiro", "marca": "Adidas", "precio_base": 39990},
            {"nombre": "Jeans Diesel", "marca": "Diesel", "precio_base": 89990}
        ],
        "Accesorios": [
            {"nombre": "Cinturón Gucci", "marca": "Gucci", "precio_base": 199990},
            {"nombre": "Bufanda Burberry", "marca": "Burberry", "precio_base": 89990},
            {"nombre": "Gorra New Era", "marca": "New Era", "precio_base": 29990},
            {"nombre": "Guantes North Face", "marca": "The North Face", "precio_base": 39990},
            {"nombre": "Cinturón Hermès", "marca": "Hermès", "precio_base": 249990}
        ]
    }
    
    colors = ["Negro", "Blanco", "Azul", "Rojo", "Verde", "Gris", "Marrón", "Beige"]
    sizes_clothing = ["XS", "S", "M", "L", "XL", "XXL"]
    sizes_shoes = ["36", "37", "38", "39", "40", "41", "42", "43", "44", "45"]
    
    total_products = 0
    total_variants = 0
    
    for cat_name, products in products_data.items():
        categoria = db.query(Categoria).filter(Categoria.nombre == cat_name).first()
        if not categoria:
            continue
            
        for product_data in products:
            # Crear producto
            producto = Producto(
                nombre=product_data["nombre"],
                id_categoria=categoria.id_categoria,
                marca=product_data["marca"]
            )
            db.add(producto)
            db.flush()  # Para obtener el ID
            
            # Crear variantes
            sizes = sizes_shoes if cat_name == "Zapatillas" else sizes_clothing
            
            for size in sizes[:4]:  # Solo algunas tallas
                for color in colors[:3]:  # Solo algunos colores
                    precio = product_data["precio_base"] + random.randint(-5000, 10000)
                    sku = f"{product_data['marca'][:3].upper()}-{size}-{color[:3].upper()}-{random.randint(1000, 9999)}"
                    
                    variante = ProductoVariante(
                        id_producto=producto.id_producto,
                        sku=sku,
                        talla=size,
                        color=color,
                        precio=precio,
                        image_url=f"https://example.com/images/{sku.lower()}.jpg"
                    )
                    db.add(variante)
                    total_variants += 1
            
            total_products += 1
    
    db.commit()
    print(f"✅ Creados {total_products} productos con {total_variants} variantes")

def populate_sample_sessions(db: Session):
    """Crear sesiones de ejemplo con detecciones y consultas"""
    
    # Obtener algunas variantes para las recomendaciones
    variantes = db.query(ProductoVariante).limit(20).all()
    
    for i in range(10):  # 10 sesiones de ejemplo
        # Crear sesión
        sesion = Sesion(
            canal=random.choice(["voz", "vision", "mixto"]),
            inicio=datetime.utcnow() - timedelta(hours=random.randint(1, 24))
        )
        db.add(sesion)
        db.flush()
        
        # Crear detecciones
        prendas = ["zapatillas", "polera", "chaqueta", "pantalón", "gorro", "gafas"]
        colores = ["negro", "blanco", "azul", "rojo", "gris"]
        rangos_etarios = ["child", "youth", "adult", "senior"]
        
        for j in range(random.randint(1, 3)):  # 1-3 detecciones por sesión
            deteccion = Deteccion(
                id_sesion=sesion.id_sesion,
                prenda=random.choice(prendas),
                color=random.choice(colores),
                rango_etario=random.choice(rangos_etarios),
                confianza=random.uniform(0.7, 0.95)
            )
            db.add(deteccion)
        
        # Crear consultas de voz
        consultas_ejemplo = [
            "Busco zapatillas deportivas",
            "¿Tienen chaquetas de invierno?",
            "Quiero algo en color azul",
            "Necesito pantalones para correr",
            "¿Cuál es el precio de esta polera?"
        ]
        
        for k in range(random.randint(1, 2)):  # 1-2 consultas por sesión
            consulta = ConsultaVoz(
                id_sesion=sesion.id_sesion,
                transcripcion=random.choice(consultas_ejemplo),
                intencion="buscar_producto",
                entidades='{"producto": "zapatillas", "color": "azul"}',
                confianza="alta",
                exito=random.choice([True, False])
            )
            db.add(consulta)
        
        # Terminar sesión
        sesion.termino = sesion.inicio + timedelta(minutes=random.randint(5, 30))
    
    db.commit()
    print("✅ Creadas 10 sesiones de ejemplo con detecciones y consultas")

def main():
    """Función principal para poblar la base de datos"""
    print("🛍️ Poblando base de datos con datos de retail...")
    
    db = get_db()
    try:
        # Verificar si ya hay datos
        existing_categories = db.query(Categoria).count()
        if existing_categories > 0:
            print(f"⚠️ Ya existen {existing_categories} categorías en la base de datos")
            print("🔄 Continuando con la población de datos...")
        
        # Poblar datos
        populate_categories(db)
        populate_products(db)
        populate_sample_sessions(db)
        
        # Mostrar estadísticas
        stats = {
            "Categorías": db.query(Categoria).count(),
            "Productos": db.query(Producto).count(),
            "Variantes": db.query(ProductoVariante).count(),
            "Sesiones": db.query(Sesion).count(),
            "Detecciones": db.query(Deteccion).count(),
            "Consultas de voz": db.query(ConsultaVoz).count()
        }
        
        print("\n📊 Estadísticas de la base de datos:")
        for key, value in stats.items():
            print(f"  {key}: {value}")
        
        print("\n🎉 ¡Base de datos poblada exitosamente!")
        
    except Exception as e:
        print(f"❌ Error al poblar la base de datos: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    main()

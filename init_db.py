"""
Script para inicializar la base de datos SQLite del NeoTotem
"""
from database.database import engine
from database.models import Base
import os

def init_database():
    """Crea todas las tablas en la base de datos"""
    try:
        # Crear todas las tablas
        Base.metadata.create_all(bind=engine)
        
        # Verificar que se creó el archivo
        db_path = "neototem.db"
        if os.path.exists(db_path):
            size = os.path.getsize(db_path)
            print(f"✅ Base de datos creada exitosamente: {db_path} ({size} bytes)")
        else:
            print("⚠️ Archivo de base de datos no encontrado")
            
        print("✅ Todas las tablas fueron creadas correctamente")
        return True
        
    except Exception as e:
        print(f"❌ Error al crear la base de datos: {e}")
        return False

if __name__ == "__main__":
    print("🗄️ Inicializando base de datos NeoTotem...")
    success = init_database()
    if success:
        print("🎉 ¡Base de datos lista para usar!")
    else:
        print("💥 Falló la inicialización de la base de datos")



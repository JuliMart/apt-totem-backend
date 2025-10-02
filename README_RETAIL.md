# 🛍️ NeoTotem Retail API

Sistema de retail inteligente con detección de prendas, análisis de voz y recomendaciones personalizadas.

## 🚀 Características

- **Detección de prendas** en tiempo real con MediaPipe
- **Análisis de voz** con procesamiento de lenguaje natural
- **Recomendaciones personalizadas** basadas en detecciones
- **Integración con APIs externas** (Fake Store API)
- **Base de datos local** con SQLite
- **API REST** completa con FastAPI
- **WebSockets** para comunicación en tiempo real

## 📦 Instalación

1. **Instalar dependencias:**
```bash
cd apt-totem-backend
pip install -r requirements.txt
```

2. **Inicializar base de datos:**
```bash
python init_db.py
```

3. **Poblar con datos de ejemplo:**
```bash
python populate_database.py
```

4. **Iniciar servidor:**
```bash
uvicorn api.main:app --reload
```

## 🗄️ Opciones de Base de Datos

### Opción 1: Poblar Base de Datos Local

Ejecuta el script para crear datos de retail realistas:

```bash
python populate_database.py
```

Esto creará:
- 10 categorías de ropa (Zapatillas, Poleras, Chaquetas, etc.)
- 25 productos con marcas conocidas
- 300+ variantes con diferentes tallas y colores
- 10 sesiones de ejemplo con detecciones y consultas de voz

### Opción 2: Conectar a API Retail Externa

Usa la integración con Fake Store API:

```bash
python test_retail_api.py
```

Esto sincronizará:
- Categorías de la API externa
- Productos con precios reales
- Imágenes de productos
- Datos actualizados automáticamente

## 🔌 Endpoints de la API

### Base de Datos Local
- `GET /productos/` - Listar productos locales
- `GET /productos/{id}` - Detalle de producto
- `GET /sesiones/` - Listar sesiones
- `GET /recomendaciones/` - Obtener recomendaciones

### API Externa (Fake Store API)
- `GET /retail-api/categories` - Categorías externas
- `GET /retail-api/products` - Productos externos
- `GET /retail-api/search?q=shirt` - Buscar productos
- `GET /retail-api/recommendations/{id}` - Recomendaciones
- `POST /retail-api/sync` - Sincronizar datos externos
- `GET /retail-api/health` - Estado de la API externa

### WebSocket
- `WS /ws` - Conexión en tiempo real para detecciones

## 🧪 Pruebas

### Probar Base de Datos Local
```bash
python test_retail_api.py
```

### Probar API Externa
```bash
# Verificar conectividad
curl http://localhost:8000/retail-api/health

# Obtener categorías
curl http://localhost:8000/retail-api/categories

# Buscar productos
curl "http://localhost:8000/retail-api/search?q=shirt"
```

### Sincronizar Datos Externos
```bash
# Sincronizar todo
curl -X POST http://localhost:8000/retail-api/sync

# Solo categorías
curl -X POST http://localhost:8000/retail-api/sync-categories

# Solo productos
curl -X POST http://localhost:8000/retail-api/sync-products
```

## 📊 Estructura de Datos

### Categorías
- Zapatillas, Poleras, Chaquetas, Pantalones, Vestidos
- Accesorios, Gorros, Gafas, Relojes, Bolsos

### Productos
- Marcas: Nike, Adidas, Converse, Vans, Puma
- Ralph Lauren, Tommy Hilfiger, Lacoste, Hugo Boss
- The North Face, Columbia, Patagonia, etc.

### Variantes
- Tallas: XS, S, M, L, XL, XXL (ropa) / 36-45 (zapatos)
- Colores: Negro, Blanco, Azul, Rojo, Verde, Gris, etc.
- Precios realistas para el mercado chileno

## 🔧 Configuración

### Variables de Entorno
Crea un archivo `.env`:
```env
DATABASE_URL=sqlite:///./neototem.db
EXTERNAL_API_URL=https://fakestoreapi.com
LOG_LEVEL=INFO
```

### Base de Datos
- **Desarrollo**: SQLite (`neototem.db`)
- **Producción**: Oracle 11g (ver `schema_oracle11g.sql`)

## 🎯 Casos de Uso

1. **Detección de Cliente**: Analizar prendas y colores en tiempo real
2. **Recomendaciones**: Sugerir productos basados en detecciones
3. **Búsqueda por Voz**: "Busco zapatillas deportivas"
4. **Sincronización**: Mantener catálogo actualizado con APIs externas
5. **Análisis**: Estadísticas de sesiones y preferencias

## 🚨 Solución de Problemas

### Error de Conexión a API Externa
```bash
# Verificar conectividad
curl https://fakestoreapi.com/products

# Revisar logs
tail -f logs/app.log
```

### Base de Datos Vacía
```bash
# Reinicializar
rm neototem.db
python init_db.py
python populate_database.py
```

### Dependencias Faltantes
```bash
# Reinstalar
pip install -r requirements.txt --force-reinstall
```

## 📈 Próximas Mejoras

- [ ] Integración con más APIs retail
- [ ] Sistema de inventario en tiempo real
- [ ] Análisis de sentimientos en consultas de voz
- [ ] Dashboard de analytics
- [ ] Notificaciones push
- [ ] Sistema de usuarios y permisos

## 🤝 Contribuir

1. Fork el proyecto
2. Crea una rama para tu feature
3. Commit tus cambios
4. Push a la rama
5. Abre un Pull Request

## 📄 Licencia

MIT License - ver archivo LICENSE para detalles.

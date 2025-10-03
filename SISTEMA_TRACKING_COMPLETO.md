# 🎯 Sistema de Tracking de Recomendaciones - COMPLETADO

## ✅ **Funcionalidades Implementadas**

### 📊 **Modelos de Base de Datos**
- **RecomendacionSesion**: Registra cada generación de recomendaciones
- **RecomendacionItem**: Detalla cada producto recomendado con métricas
- **InteraccionUsuario**: Registra todas las interacciones del usuario
- **MetricasSesion**: Calcula métricas agregadas por sesión

### 🔍 **Tracking Automático**
- **Generación de recomendaciones**: Tiempo, algoritmo, filtros aplicados
- **Vistas de productos**: Duración, posición, contexto
- **Clics en productos**: Posición, timestamp, recomendación asociada
- **Interacciones generales**: Scroll, hover, búsquedas, etc.

### 📈 **Sistema de Analytics**
- **Métricas por sesión**: CTR, tiempo promedio, productos más clicados
- **Rendimiento general**: Análisis de algoritmos, tipos de recomendación
- **Productos top**: Ranking por clics y engagement
- **Dashboard completo**: Vista consolidada de todas las métricas

## 🚀 **Endpoints Disponibles**

### **Recomendaciones con Tracking**
```
GET /recomendaciones/?session_id={uuid}&categoria=Zapatillas
GET /recomendaciones/categoria/{categoria}?session_id={uuid}
GET /recomendaciones/marca/{marca}?session_id={uuid}
GET /recomendaciones/personalizadas?edad=18-25&session_id={uuid}
GET /recomendaciones/similar/{product_id}?session_id={uuid}
GET /recomendaciones/cross-sell/{product_id}?session_id={uuid}
```

### **Analytics y Métricas**
```
GET /analytics/sesion/{session_id}/metricas
GET /analytics/rendimiento?dias=7&tipo_recomendacion=categoria
GET /analytics/productos-top?dias=7&limite=10
GET /analytics/dashboard?dias=7
```

### **Tracking de Interacciones**
```
POST /analytics/track/view?session_id={uuid}&variant_id={id}&view_duration_seconds=2.5
POST /analytics/track/click?session_id={uuid}&variant_id={id}&click_position=1
POST /analytics/track/interaction?session_id={uuid}&interaction_type=scroll
```

### **Exportación de Datos**
```
GET /analytics/export/{session_id}?formato=json
GET /analytics/export/{session_id}?formato=csv
```

## 📊 **Métricas Capturadas**

### **Por Recomendación**
- Tipo de recomendación (categoría, marca, color, personalizada, etc.)
- Algoritmo utilizado (category_filter, similar_products, etc.)
- Filtros aplicados (JSON con parámetros)
- Tiempo de generación en milisegundos
- Total de productos recomendados

### **Por Producto Recomendado**
- Posición en la lista de recomendaciones
- Score del algoritmo de recomendación
- Si fue mostrado al usuario
- Si fue clicado por el usuario
- Tiempo de visualización en segundos
- Timestamp del clic

### **Por Interacción del Usuario**
- Tipo de interacción (view, click, hover, scroll, search)
- Producto asociado (si aplica)
- Duración de la interacción
- Metadatos adicionales (JSON)
- Timestamp de la interacción

### **Métricas Agregadas por Sesión**
- Total de recomendaciones generadas
- Total de productos mostrados
- Total de clics realizados
- Tasa de clic (CTR = clics / productos mostrados)
- Tiempo promedio de visualización
- Top 5 productos más clicados
- Top 5 categorías más populares

## 🎯 **Casos de Uso**

### **1. Análisis de Rendimiento**
```bash
# Ver rendimiento de recomendaciones por categoría
curl "http://127.0.0.1:8000/analytics/rendimiento?dias=7&tipo_recomendacion=categoria"

# Ver productos más exitosos
curl "http://127.0.0.1:8000/analytics/productos-top?dias=7&limite=10"
```

### **2. Tracking en Tiempo Real**
```bash
# Generar recomendación con tracking
curl "http://127.0.0.1:8000/recomendaciones/categoria/Zapatillas?session_id=abc123&limit=5"

# Registrar vista de producto
curl -X POST "http://127.0.0.1:8000/analytics/track/view?session_id=abc123&variant_id=1&view_duration_seconds=2.5"

# Registrar clic
curl -X POST "http://127.0.0.1:8000/analytics/track/click?session_id=abc123&variant_id=1&click_position=1"
```

### **3. Dashboard de Analytics**
```bash
# Dashboard completo
curl "http://127.0.0.1:8000/analytics/dashboard?dias=7"

# Métricas de sesión específica
curl "http://127.0.0.1:8000/analytics/sesion/abc123/metricas"
```

## 🔧 **Integración con Frontend**

### **Flutter/Dart**
```dart
// Generar recomendación con tracking
final response = await http.get(
  Uri.parse('http://127.0.0.1:8000/recomendaciones/categoria/Zapatillas?session_id=$sessionId&limit=5')
);

// Registrar vista de producto
await http.post(
  Uri.parse('http://127.0.0.1:8000/analytics/track/view'),
  body: {
    'session_id': sessionId,
    'variant_id': productId.toString(),
    'view_duration_seconds': viewDuration.toString(),
  }
);

// Registrar clic
await http.post(
  Uri.parse('http://127.0.0.1:8000/analytics/track/click'),
  body: {
    'session_id': sessionId,
    'variant_id': productId.toString(),
    'click_position': position.toString(),
  }
);
```

## 📈 **Beneficios del Sistema**

1. **Análisis de Comportamiento**: Entender qué productos y categorías prefieren los usuarios
2. **Optimización de Algoritmos**: Mejorar recomendaciones basándose en datos reales
3. **Métricas de Engagement**: Medir efectividad de diferentes tipos de recomendaciones
4. **Personalización**: Ajustar recomendaciones según patrones de interacción
5. **ROI de Recomendaciones**: Medir impacto en conversiones y ventas
6. **A/B Testing**: Comparar rendimiento de diferentes algoritmos
7. **Reportes Ejecutivos**: Dashboard con métricas clave para toma de decisiones

## 🎉 **¡Sistema Completo y Funcional!**

El sistema de tracking de recomendaciones está completamente implementado y probado. Todas las recomendaciones generadas quedan registradas automáticamente, permitiendo extraer métricas detalladas para análisis posterior y optimización del sistema de recomendaciones.

**Servidor activo en**: http://127.0.0.1:8000
**Documentación interactiva**: http://127.0.0.1:8000/docs





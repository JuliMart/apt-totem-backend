from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from api.routers import asr, cv, productos, sesiones, recomendaciones, analytics, busqueda
from services.ai.real_detection import analyze_realtime_stream_real
from services.nlu.heuristics import extract_intent_advanced
import json
import asyncio
from datetime import datetime
from typing import List

app = FastAPI(title="NeoTotem API - Tiempo Real con MediaPipe")

# Agregar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Incluir routers
app.include_router(asr.router)
app.include_router(cv.router)
app.include_router(productos.router)
app.include_router(sesiones.router)
app.include_router(recomendaciones.router)
app.include_router(analytics.router)
app.include_router(busqueda.router)

# Lista de conexiones WebSocket activas
active_connections: List[WebSocket] = []

class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def send_personal_message(self, message: str, websocket: WebSocket):
        await websocket.send_text(message)

    async def broadcast(self, message: str):
        for connection in self.active_connections:
            await connection.send_text(message)

manager = ConnectionManager()

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    
    # Enviar mensaje de bienvenida
    welcome_msg = {
        "type": "connected",
        "message": "🔗 NeoTotem Retail conectado - Detección REAL activada",
        "features": ["deteccion_real_prendas", "analisis_colores", "estimacion_edad", "recomendaciones_personalizadas"],
        "timestamp": datetime.now().isoformat()
    }
    await manager.send_personal_message(json.dumps(welcome_msg), websocket)
    
    try:
        while True:
            # Recibir datos del cliente
            data = await websocket.receive_text()
            message = json.loads(data)
            
            # Procesar diferentes tipos de mensajes
            if message["type"] == "voice":
                # Procesamiento NLU avanzado
                text = message.get("text", "")
                intent, entities, confidence = extract_intent_advanced(text)
                
                response = {
                    "type": "voice_analysis",
                    "original_text": text,
                    "intent": intent,
                    "entities": entities,
                    "confidence": round(confidence, 2),
                    "timestamp": datetime.now().isoformat(),
                    "analysis_engine": "nlu_advanced"
                }
                await manager.send_personal_message(json.dumps(response), websocket)
                
            elif message["type"] == "image_stream":
                # Análisis de imagen en tiempo real con MediaPipe
                try:
                    image_data = message.get("image_data", "")
                    camera_active = message.get("camera_active", False)
                    
                    if image_data and camera_active:
                        # Análisis REAL con imagen de la cámara
                        analysis = analyze_realtime_stream_real(image_data)
                        
                        response = {
                            "type": "realtime_analysis",
                            "analysis": analysis,
                            "timestamp": datetime.now().isoformat(),
                            "engine": "real_detection_mediapipe",
                            "camera_source": "real"
                        }
                    else:
                        # Análisis específico para RETAIL: prendas, colores y edad
                        import random
                        
                        # Datos específicos para retail/fashion
                        age_ranges = ["18-25", "26-35", "36-45", "46-55", "55+"]
                        clothing_types = ["casual", "formal", "deportivo", "elegante", "juvenil"]
                        colors_detected = ["azul", "negro", "blanco", "rojo", "verde", "gris", "beige", "marron"]
                        clothing_items = ["camiseta", "pantalon", "chaqueta", "vestido", "falda", "zapatos", "accesorios"]
                        
                        # Simulación de análisis de prendas y colores
                        person_detected = random.choice([True, True, True, False])  # 75% probabilidad
                        age_range = random.choice(age_ranges)
                        clothing_style = random.choice(clothing_types)
                        primary_color = random.choice(colors_detected)
                        secondary_color = random.choice(colors_detected) if random.random() > 0.5 else None
                        clothing_item = random.choice(clothing_items)
                        confidence = random.uniform(0.6, 0.95)
                        
                        # Recomendaciones basadas en análisis de prendas
                        if age_range in ["18-25", "26-35"]:
                            recommended_categories = ["moda_joven", "casual", "deportivo"]
                        elif age_range in ["36-45", "46-55"]:
                            recommended_categories = ["profesional", "elegante", "casual"]
                        else:
                            recommended_categories = ["clasico", "comodo", "elegante"]
                        
                        response = {
                            "type": "realtime_analysis",
                            "analysis": {
                                "person_detected": person_detected,
                                "age_range": age_range,
                                "clothing_style": clothing_style,
                                "primary_color": primary_color,
                                "secondary_color": secondary_color,
                                "clothing_item": clothing_item,
                                "detection_confidence": round(confidence, 2),
                                "recommendations": {
                                    "target_categories": recommended_categories,
                                    "color_preference": primary_color,
                                    "style_suggestion": clothing_style,
                                    "age_appropriate": True,
                                    "interaction_tips": [
                                        f"Cliente {age_range} años - estilo {clothing_style}",
                                        f"Color principal: {primary_color}",
                                        f"Recomendar: {', '.join(recommended_categories)}"
                                    ]
                                }
                            },
                            "timestamp": datetime.now().isoformat(),
                            "engine": "retail_fashion_analysis",
                            "camera_source": "simulated"
                        }
                    
                    await manager.send_personal_message(json.dumps(response), websocket)
                    
                except Exception as e:
                    error_response = {
                        "type": "analysis_error",
                        "error": str(e),
                        "timestamp": datetime.now().isoformat()
                    }
                    await manager.send_personal_message(json.dumps(error_response), websocket)
            
            elif message["type"] == "ping":
                # Mantener conexión viva
                pong_response = {
                    "type": "pong",
                    "timestamp": datetime.now().isoformat()
                }
                await manager.send_personal_message(json.dumps(pong_response), websocket)
                
    except WebSocketDisconnect:
        manager.disconnect(websocket)
        print(f"Cliente desconectado: {websocket.client}")

@app.get("/")
def read_root():
    return {
        "message": "🛍️ NeoTotem Retail API con DETECCIÓN REAL funcionando", 
        "version": "3.0", 
        "status": "active",
        "features": {
            "websockets": True,
            "real_detection": True,
            "real_time": True,
            "voice_analysis": True,
            "computer_vision": True,
            "clothing_detection": True,
            "color_analysis": True,
            "age_estimation": True
        }
    }


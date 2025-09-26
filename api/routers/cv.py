from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from sqlalchemy.orm import Session
from database import models, database
from api.schemas import ColorResponse
from services.cv.color import detect_dominant_hsv
from services.ai.real_detection import analyze_realtime_stream_real
from services.ai.yolo_clothing_detector import analyze_clothing_with_yolo
import numpy as np, cv2 as cv
import random
import base64
from datetime import datetime

router = APIRouter(prefix="/cv", tags=["Visión"])

MAX_IMAGE_BYTES = 8 * 1024 * 1024

@router.post("/detect-frame", response_model=ColorResponse)
async def detect_frame(file: UploadFile = File(...), id_sesion: str = None, db: Session = Depends(database.get_db)):
    if file.content_type not in {"image/jpeg","image/png"}:
        raise HTTPException(415, "Formato no soportado")

    img_bytes = await file.read()
    if len(img_bytes) > MAX_IMAGE_BYTES:
        raise HTTPException(413, "Imagen demasiado grande")

    nparr = np.frombuffer(img_bytes, np.uint8)
    img = cv.imdecode(nparr, cv.IMREAD_COLOR)
    if img is None:
        raise HTTPException(400, "Imagen inválida")

    res = detect_dominant_hsv(img)

    if id_sesion:
        deteccion = models.Deteccion(
            id_sesion=id_sesion,
            prenda="camiseta",
            color=res["color_name"],
            rango_etario="adulto",
            confianza=0.9
        )
        db.add(deteccion)
        db.commit()

    return ColorResponse(**res)

@router.post("/analyze-customer-ai-real")
async def analyze_customer_ai_real(file: UploadFile = File(...), id_sesion: str = None, db: Session = Depends(database.get_db)):
    """
    Endpoint para análisis REAL de cliente con IA NeoTotem
    Detecta prendas reales, estima edad, analiza colores y genera recomendaciones
    """
    if file.content_type not in {"image/jpeg","image/png","image/jpg"}:
        raise HTTPException(415, "Formato de imagen no soportado")
    
    img_bytes = await file.read()
    if len(img_bytes) > MAX_IMAGE_BYTES:
        raise HTTPException(413, "Imagen demasiado grande")
    
    try:
        # Convertir imagen a base64 para el análisis real
        image_base64 = base64.b64encode(img_bytes).decode('utf-8')
        
        # Realizar análisis REAL con MediaPipe y OpenCV
        analysis = analyze_realtime_stream_real(image_base64)
        
        # Guardar detección en base de datos si hay sesión
        if id_sesion and analysis.get("person_detected", False):
            deteccion = models.Deteccion(
                id_sesion=id_sesion,
                prenda=analysis.get("clothing_item", "desconocido"),
                color=analysis.get("primary_color", "desconocido"),
                rango_etario=analysis.get("age_range", "desconocido"),
                confianza=analysis.get("detection_confidence", 0.0)
            )
            db.add(deteccion)
            db.commit()
        
        return analysis
        
    except Exception as e:
        raise HTTPException(500, f"Error en análisis de IA: {str(e)}")

@router.get("/analyze-customer-ai")
async def analyze_customer_ai_demo():
    """
    Endpoint DEMO para análisis de cliente (sin imagen)
    Retorna datos de ejemplo para testing
    """
    emotions = ["feliz", "neutral", "concentrado", "interesado", "sorprendido"]
    age_ranges = ["18-25", "26-35", "36-45", "46-55", "55+"]
    clothing_items = ["camiseta", "chaqueta", "polo", "blusa", "vestido"]
    colors = ["azul", "rojo", "verde", "negro", "blanco", "gris"]
    
    return {
        "person_detected": random.choice([True, True, True, False]),
        "age_range": random.choice(age_ranges),
        "emotion": random.choice(emotions),
        "clothing_item": random.choice(clothing_items),
        "primary_color": random.choice(colors),
        "clothing_style": random.choice(["casual", "formal", "deportivo", "elegante"]),
        "engagement": round(random.uniform(0.3, 0.9), 2),
        "confidence": round(random.uniform(0.7, 0.95), 2),
        "timestamp": "2024-01-01T00:00:00Z",
        "analysis_type": "neototem_demo_mode"
    }

@router.post("/detect-clothing")
async def detect_clothing_real(file: UploadFile = File(...), id_sesion: str = None, db: Session = Depends(database.get_db)):
    """
    Endpoint especializado para detección REAL de prendas
    Analiza específicamente ropa, colores y estilos
    """
    if file.content_type not in {"image/jpeg","image/png","image/jpg"}:
        raise HTTPException(415, "Formato de imagen no soportado")
    
    img_bytes = await file.read()
    if len(img_bytes) > MAX_IMAGE_BYTES:
        raise HTTPException(413, "Imagen demasiado grande")
    
    try:
        # Convertir imagen a base64
        image_base64 = base64.b64encode(img_bytes).decode('utf-8')
        
        # Análisis especializado de prendas
        analysis = analyze_realtime_stream_real(image_base64)
        
        # Extraer información específica de prendas
        clothing_analysis = {
            "timestamp": analysis.get("timestamp"),
            "person_detected": analysis.get("person_detected", False),
            "clothing_detected": analysis.get("clothing_item", "desconocido"),
            "primary_color": analysis.get("primary_color", "desconocido"),
            "secondary_color": analysis.get("secondary_color"),
            "clothing_style": analysis.get("clothing_style", "desconocido"),
            "age_range": analysis.get("age_range", "desconocido"),
            "confidence": analysis.get("detection_confidence", 0.0),
            "recommendations": analysis.get("recommendations", {}),
            "analysis_type": "neototem_clothing_detection"
        }
        
        # Guardar en base de datos
        if id_sesion and analysis.get("person_detected", False):
            deteccion = models.Deteccion(
                id_sesion=id_sesion,
                prenda=analysis.get("clothing_item", "desconocido"),
                color=analysis.get("primary_color", "desconocido"),
                rango_etario=analysis.get("age_range", "desconocido"),
                confianza=analysis.get("detection_confidence", 0.0)
            )
            db.add(deteccion)
            db.commit()
        
        return clothing_analysis
        
    except Exception as e:
        raise HTTPException(500, f"Error en detección de prendas: {str(e)}")

@router.post("/detect-clothing-yolo")
async def detect_clothing_yolo(file: UploadFile = File(...), id_sesion: str = None, db: Session = Depends(database.get_db)):
    """
    Endpoint para detección AVANZADA de prendas usando YOLO
    Análisis más preciso con modelos especializados en ropa
    """
    if file.content_type not in {"image/jpeg","image/png","image/jpg"}:
        raise HTTPException(415, "Formato de imagen no soportado")
    
    img_bytes = await file.read()
    if len(img_bytes) > MAX_IMAGE_BYTES:
        raise HTTPException(413, "Imagen demasiado grande")
    
    try:
        # Convertir imagen a base64
        image_base64 = base64.b64encode(img_bytes).decode('utf-8')
        
        # Análisis avanzado con YOLO
        analysis = analyze_clothing_with_yolo(image_base64)
        
        # Procesar resultados
        yolo_result = {
            "timestamp": analysis.get("timestamp"),
            "person_detected": analysis.get("person_detected", False),
            "clothing_items": analysis.get("clothing_items", []),
            "primary_clothing": analysis.get("primary_clothing", "desconocido"),
            "clothing_style": analysis.get("clothing_style", "desconocido"),
            "primary_color": analysis.get("primary_color", "desconocido"),
            "secondary_color": analysis.get("secondary_color"),
            "confidence": analysis.get("confidence", 0.0),
            "color_confidence": analysis.get("color_confidence", 0.0),
            "detection_method": analysis.get("detection_method", "yolo"),
            "analysis_type": analysis.get("analysis_type", "yolo_clothing_detection")
        }
        
        # Guardar en base de datos
        if id_sesion and analysis.get("person_detected", False):
            deteccion = models.Deteccion(
                id_sesion=id_sesion,
                prenda=analysis.get("primary_clothing", "desconocido"),
                color=analysis.get("primary_color", "desconocido"),
                rango_etario="adulto",  # YOLO no estima edad directamente
                confianza=analysis.get("confidence", 0.0)
            )
            db.add(deteccion)
            db.commit()
        
        return yolo_result
        
    except Exception as e:
        raise HTTPException(500, f"Error en detección YOLO: {str(e)}")

@router.post("/analyze-complete")
async def analyze_complete_customer(file: UploadFile = File(...), id_sesion: str = None, db: Session = Depends(database.get_db)):
    """
    Endpoint COMPLETO que combina MediaPipe + YOLO para análisis integral
    Máxima precisión en detección de prendas, colores y comportamiento
    """
    if file.content_type not in {"image/jpeg","image/png","image/jpg"}:
        raise HTTPException(415, "Formato de imagen no soportado")
    
    img_bytes = await file.read()
    if len(img_bytes) > MAX_IMAGE_BYTES:
        raise HTTPException(413, "Imagen demasiado grande")
    
    try:
        # Convertir imagen a base64
        image_base64 = base64.b64encode(img_bytes).decode('utf-8')
        
        # Análisis con MediaPipe (comportamiento y edad)
        mediapipe_result = analyze_realtime_stream_real(image_base64)
        
        # Análisis con YOLO (prendas específicas)
        yolo_result = analyze_clothing_with_yolo(image_base64)
        
        # FORZAR detección de accesorio de cabeza si hay persona detectada
        person_detected = mediapipe_result.get("person_detected", False) or yolo_result.get("person_detected", False)
        
        # Detectar accesorios de cabeza usando MediaPipe (más confiable)
        if person_detected:
            # Verificar si MediaPipe detectó un accesorio de cabeza
            mediapipe_clothing = mediapipe_result.get("clothing_item", "").lower()
            head_accessory_keywords = ["gorro", "gorra", "jockey", "sombrero", "gafas"]
            
            if any(keyword in mediapipe_clothing for keyword in head_accessory_keywords):
                # MediaPipe detectó un accesorio de cabeza
                head_accessories = [mediapipe_clothing]
                primary_clothing = mediapipe_clothing
                primary_type = "accesorio_cabeza"
                clothing_style = mediapipe_result.get("clothing_style", "casual")
            else:
                # No hay accesorio de cabeza detectado, usar YOLO para prendas corporales
                yolo_head_accessories = yolo_result.get("head_accessories", [])
                yolo_body_clothing = yolo_result.get("body_clothing", [])
                
                if yolo_head_accessories:
                    # YOLO detectó accesorios (backup)
                    head_accessories = yolo_head_accessories
                    primary_clothing = yolo_result.get("primary_clothing", "desconocido")
                    primary_type = "accesorio_cabeza"
                    clothing_style = yolo_result.get("clothing_style", "casual")
                else:
                    # Solo prendas corporales
                    head_accessories = []
                    primary_clothing = yolo_result.get("primary_clothing", "camiseta")
                    primary_type = "prenda_corporal"
                    clothing_style = yolo_result.get("clothing_style", "casual")
        else:
            head_accessories = []
            primary_clothing = yolo_result.get("primary_clothing", "desconocido")
            primary_type = yolo_result.get("primary_type", "general")
            clothing_style = yolo_result.get("clothing_style", "desconocido")
        
        # Combinar resultados para análisis completo
        complete_analysis = {
            "timestamp": datetime.now().isoformat(),
            "person_detected": person_detected,
            
            # Información de prendas (YOLO + FORZADA)
            "clothing_items": yolo_result.get("clothing_items", []),
            "primary_clothing": primary_clothing,
            "primary_type": primary_type,
            "head_accessories": head_accessories,
            "body_clothing": yolo_result.get("body_clothing", []),
            "clothing_style": clothing_style,
            
            # Información de colores (YOLO + MediaPipe)
            "primary_color": yolo_result.get("primary_color") or mediapipe_result.get("primary_color", "desconocido"),
            "secondary_color": yolo_result.get("secondary_color") or mediapipe_result.get("secondary_color"),
            
            # Información demográfica (MediaPipe)
            "age_range": mediapipe_result.get("age_range", "desconocido"),
            "emotion": mediapipe_result.get("emotion", "neutral"),
            
            # Confianza combinada
            "clothing_confidence": yolo_result.get("confidence", 0.0),
            "behavior_confidence": mediapipe_result.get("detection_confidence", 0.0),
            "overall_confidence": (yolo_result.get("confidence", 0.0) + mediapipe_result.get("detection_confidence", 0.0)) / 2,
            
            # Recomendaciones combinadas
            "recommendations": mediapipe_result.get("recommendations", {}),
            
            # Metadatos
            "analysis_type": "neototem_complete_analysis",
            "detection_methods": ["mediapipe", "yolo"],
            "processing_time": "real_time"
        }
        
        # Guardar en base de datos
        if id_sesion and complete_analysis.get("person_detected", False):
            deteccion = models.Deteccion(
                id_sesion=id_sesion,
                prenda=complete_analysis.get("primary_clothing", "desconocido"),
                color=complete_analysis.get("primary_color", "desconocido"),
                rango_etario=complete_analysis.get("age_range", "desconocido"),
                confianza=complete_analysis.get("overall_confidence", 0.0)
            )
            db.add(deteccion)
            db.commit()
        
        return complete_analysis
        
    except Exception as e:
        raise HTTPException(500, f"Error en análisis completo: {str(e)}")

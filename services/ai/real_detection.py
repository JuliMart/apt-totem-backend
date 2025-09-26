import cv2
import mediapipe as mp
import numpy as np
from datetime import datetime
import base64
from collections import Counter
from sklearn.cluster import KMeans
from typing import Dict, Any, Optional

# Inicializar MediaPipe
mp_face_detection = mp.solutions.face_detection
mp_pose = mp.solutions.pose
mp_drawing = mp.solutions.drawing_utils

def analyze_real_clothing(image_np: np.ndarray) -> dict:
    """
    Análisis REAL de prendas usando MediaPipe y OpenCV.
    """
    results = {
        "timestamp": datetime.now().isoformat(),
        "person_detected": False,
        "face_detected": False,
        "pose_detected": False,
        "age_range": "desconocido",
        "clothing_style": "casual",
        "primary_color": "desconocido",
        "secondary_color": None,
        "clothing_item": "desconocido",
        "detection_confidence": 0.0,
        "details": {}
    }

    # Convertir la imagen a RGB para MediaPipe
    image_rgb = cv2.cvtColor(image_np, cv2.COLOR_BGR2RGB)
    height, width, _ = image_np.shape

    # Detección facial para estimar edad
    with mp_face_detection.FaceDetection(model_selection=1, min_detection_confidence=0.5) as face_detection:
        face_results = face_detection.process(image_rgb)
        if face_results.detections:
            results["person_detected"] = True
            results["face_detected"] = True
            results["detection_confidence"] = max([detection.score for detection in face_results.detections])
            
            # Estimación básica de edad basada en características faciales
            for detection in face_results.detections:
                bbox = detection.location_data.relative_bounding_box
                face_width = bbox.width
                face_height = bbox.height
                
                # Heurística simple para estimar edad basada en proporciones faciales
                if face_width > 0.15 and face_height > 0.15:  # Cara grande = adulto
                    results["age_range"] = "36-45"
                elif face_width > 0.12 and face_height > 0.12:  # Cara mediana = adulto joven
                    results["age_range"] = "26-35"
                else:  # Cara pequeña = joven
                    results["age_range"] = "18-25"
            
            results["details"]["face_detections"] = len(face_results.detections)

    # Detección de pose para identificar tipo de prenda
    with mp_pose.Pose(min_detection_confidence=0.5, min_tracking_confidence=0.5) as pose:
        pose_results = pose.process(image_rgb)
        if pose_results.pose_landmarks:
            results["person_detected"] = True
            results["pose_detected"] = True
            
            # Analizar landmarks para determinar tipo de prenda
            landmarks = pose_results.pose_landmarks.landmark
            
            # Detectar si lleva camiseta (basado en landmarks de hombros y torso)
            left_shoulder = landmarks[11]  # LEFT_SHOULDER
            right_shoulder = landmarks[12]  # RIGHT_SHOULDER
            left_hip = landmarks[23]  # LEFT_HIP
            right_hip = landmarks[24]  # RIGHT_HIP
            
            # Calcular distancia entre hombros para determinar tipo de prenda
            shoulder_distance = abs(left_shoulder.x - right_shoulder.x)
            hip_distance = abs(left_hip.x - right_hip.x)
            
            if shoulder_distance > 0.15:  # Hombros anchos = chaqueta o abrigo
                results["clothing_item"] = "chaqueta"
                results["clothing_style"] = "formal"
            elif shoulder_distance > 0.12:  # Hombros normales = camiseta
                results["clothing_item"] = "camiseta"
                results["clothing_style"] = "casual"
            else:  # Hombros estrechos = prenda ajustada
                results["clothing_item"] = "camiseta"
                results["clothing_style"] = "juvenil"
            
            results["details"]["pose_landmarks_count"] = len(landmarks)

    # Análisis de colores dominantes usando K-means
    try:
        # Redimensionar imagen para análisis más rápido
        small_image = cv2.resize(image_np, (150, 150))
        pixels = small_image.reshape(-1, 3)
        
        # Aplicar K-means para encontrar colores dominantes
        kmeans = KMeans(n_clusters=3, random_state=42, n_init=10)
        kmeans.fit(pixels)
        
        # Obtener colores dominantes
        colors = kmeans.cluster_centers_.astype(int)
        labels = kmeans.labels_
        
        # Contar frecuencia de cada color
        label_counts = Counter(labels)
        
        # Convertir colores BGR a nombres
        color_names = []
        for color in colors:
            b, g, r = color
            color_name = get_color_name(r, g, b)
            color_names.append(color_name)
        
        # Asignar colores principales
        if len(color_names) > 0:
            results["primary_color"] = color_names[0]
        if len(color_names) > 1:
            results["secondary_color"] = color_names[1]
        
        results["details"]["dominant_colors"] = color_names
        results["details"]["color_counts"] = dict(label_counts)
        
    except Exception as e:
        print(f"Error en análisis de colores: {e}")
        results["primary_color"] = "desconocido"

    return results

def get_color_name(r: int, g: int, b: int) -> str:
    """
    Convierte valores RGB a nombres de colores aproximados.
    """
    # Definir rangos de colores
    color_ranges = {
        "rojo": [(150, 0, 0), (255, 100, 100)],
        "azul": [(0, 0, 150), (100, 100, 255)],
        "verde": [(0, 150, 0), (100, 255, 100)],
        "negro": [(0, 0, 0), (50, 50, 50)],
        "blanco": [(200, 200, 200), (255, 255, 255)],
        "gris": [(100, 100, 100), (150, 150, 150)],
        "marron": [(100, 50, 0), (150, 100, 50)],
        "beige": [(200, 180, 150), (255, 220, 180)],
    }
    
    for color_name, (min_rgb, max_rgb) in color_ranges.items():
        if (min_rgb[0] <= r <= max_rgb[0] and 
            min_rgb[1] <= g <= max_rgb[1] and 
            min_rgb[2] <= b <= max_rgb[2]):
            return color_name
    
    return "desconocido"

def analyze_realtime_stream_real(image_data_base64: str) -> dict:
    """
    Análisis REAL de imagen usando MediaPipe y OpenCV.
    Versión simplificada para evitar problemas de serialización JSON.
    """
    if not image_data_base64:
        return {
            "person_detected": False,
            "face_detected": False,
            "pose_detected": False,
            "age_range": "unknown",
            "clothing_style": "unknown",
            "primary_color": "unknown",
            "secondary_color": None,
            "clothing_item": "unknown",
            "detection_confidence": 0.0,
            "recommendations": {
                "target_categories": [],
                "color_preference": "unknown",
                "style_suggestion": "unknown",
                "age_appropriate": False,
                "interaction_tips": ["Esperando imagen de cámara..."]
            }
        }
    
    try:
        # Decodificar la imagen base64
        img_bytes = base64.b64decode(image_data_base64)
        img_np = np.frombuffer(img_bytes, np.uint8)
        image = cv2.imdecode(img_np, cv2.IMREAD_COLOR)

        if image is None:
            raise ValueError("No se pudo decodificar la imagen base64.")

        # Análisis simplificado para evitar problemas de serialización
        analysis = analyze_real_clothing_simple(image)
        
        return analysis
        
    except Exception as e:
        print(f"Error en análisis real: {e}")
        return {
            "person_detected": False,
            "face_detected": False,
            "pose_detected": False,
            "age_range": "error",
            "clothing_style": "error",
            "primary_color": "error",
            "secondary_color": None,
            "clothing_item": "error",
            "detection_confidence": 0.0,
            "recommendations": {
                "target_categories": [],
                "color_preference": "error",
                "style_suggestion": "error",
                "age_appropriate": False,
                "interaction_tips": [f"Error en análisis: {str(e)}"]
            }
        }

def analyze_real_clothing_simple(image_np: np.ndarray) -> dict:
    """
    Análisis simplificado de prendas que evita problemas de serialización JSON.
    """
    results = {
        "timestamp": datetime.now().isoformat(),
        "person_detected": False,
        "face_detected": False,
        "pose_detected": False,
        "age_range": "desconocido",
        "clothing_style": "casual",
        "primary_color": "desconocido",
        "secondary_color": None,
        "clothing_item": "desconocido",
        "detection_confidence": 0.0,
        "recommendations": {
            "target_categories": ["casual", "elegante", "clasico"],
            "color_preference": "desconocido",
            "style_suggestion": "casual",
            "age_appropriate": True,
            "interaction_tips": ["Análisis básico completado"]
        }
    }

    try:
        # Convertir la imagen a RGB para MediaPipe
        image_rgb = cv2.cvtColor(image_np, cv2.COLOR_BGR2RGB)
        height, width, _ = image_np.shape

        # Detección facial simplificada
        with mp_face_detection.FaceDetection(model_selection=1, min_detection_confidence=0.5) as face_detection:
            face_results = face_detection.process(image_rgb)
            if face_results.detections:
                results["person_detected"] = True
                results["face_detected"] = True
                results["detection_confidence"] = float(face_results.detections[0].score[0])
                
                # Estimación básica de edad
                bbox = face_results.detections[0].location_data.relative_bounding_box
                face_width = bbox.width
                face_height = bbox.height
                
                if face_width > 0.15 and face_height > 0.15:
                    results["age_range"] = "36-45"
                elif face_width > 0.12 and face_height > 0.12:
                    results["age_range"] = "26-35"
                else:
                    results["age_range"] = "18-25"

        # Detección de pose simplificada
        with mp_pose.Pose(min_detection_confidence=0.5, min_tracking_confidence=0.5) as pose:
            pose_results = pose.process(image_rgb)
            if pose_results.pose_landmarks:
                results["person_detected"] = True
                results["pose_detected"] = True
                
                # Análisis básico de prendas
                landmarks = pose_results.pose_landmarks.landmark
                left_shoulder = landmarks[11]
                right_shoulder = landmarks[12]
                
                shoulder_distance = abs(left_shoulder.x - right_shoulder.x)
                
                if shoulder_distance > 0.15:
                    results["clothing_item"] = "chaqueta"
                    results["clothing_style"] = "formal"
                elif shoulder_distance > 0.12:
                    results["clothing_item"] = "camiseta"
                    results["clothing_style"] = "casual"
                else:
                    results["clothing_item"] = "camiseta"
                    results["clothing_style"] = "juvenil"

        # Detección INTELIGENTE de accesorios de cabeza
        # Solo detecta cuando hay evidencia clara de accesorio
        try:
            head_accessory = _detect_head_accessories_smart(image_rgb)
            if head_accessory:
                results["clothing_item"] = head_accessory
                # Ajustar estilo basado en accesorio de cabeza
                if head_accessory in ["gorra_deportiva", "jockey"]:
                    results["clothing_style"] = "deportivo"
                elif head_accessory in ["sombrero", "gafas_sol"]:
                    results["clothing_style"] = "elegante"
                elif head_accessory == "gorro":
                    results["clothing_style"] = "casual"
        except Exception as e:
            print(f"Error detectando accesorios de cabeza: {e}")

        # Análisis de colores simplificado
        try:
            small_image = cv2.resize(image_np, (100, 100))
            pixels = small_image.reshape(-1, 3)
            
            kmeans = KMeans(n_clusters=3, random_state=42, n_init=10)
            kmeans.fit(pixels)
            
            colors = kmeans.cluster_centers_.astype(int)
            
            # Convertir solo el primer color
            if len(colors) > 0:
                b, g, r = colors[0]
                results["primary_color"] = get_color_name(r, g, b)
            
        except Exception as e:
            print(f"Error en análisis de colores: {e}")
            results["primary_color"] = "desconocido"

        return results
        
    except Exception as e:
        print(f"Error en análisis simplificado: {e}")
        return results

def _detect_head_accessories_smart(image_rgb: np.ndarray) -> Optional[str]:
    """
    Detecta accesorios de cabeza usando análisis INTELIGENTE
    Requiere múltiples evidencias para evitar falsos positivos
    """
    try:
        height, width = image_rgb.shape[:2]
        
        # Analizar solo la parte superior de la imagen (30% superior)
        head_region = image_rgb[0:int(height * 0.3), :]
        
        # Convertir a escala de grises para análisis
        gray_head = cv2.cvtColor(head_region, cv2.COLOR_RGB2GRAY)
        
        # Aplicar filtros para detectar bordes
        edges = cv2.Canny(gray_head, 50, 150)
        
        # Encontrar contornos
        contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        # Contar evidencias de accesorios
        gorro_evidence = 0
        gorra_evidence = 0
        
        # Analizar contornos para detectar accesorios
        for contour in contours:
            area = cv2.contourArea(contour)
            if area > 500:  # Contornos medianos (menos estricto)
                
                # Calcular características del contorno
                perimeter = cv2.arcLength(contour, True)
                if perimeter == 0:
                    continue
                    
                circularity = 4 * np.pi * area / (perimeter * perimeter)
                x, y, w, h = cv2.boundingRect(contour)
                rectangularity = area / (w * h)
                aspect_ratio = w / h if h > 0 else 0
                
                # EVIDENCIA DE GORRO: Requiere múltiples características
                if (circularity > 0.3 and 
                    rectangularity > 0.4 and 
                    aspect_ratio < 1.5 and 
                    area > 1000):
                    gorro_evidence += 1
                
                # EVIDENCIA DE GORRA: Formas más rectangulares
                elif (circularity > 0.3 and 
                      aspect_ratio > 1.5 and 
                      rectangularity > 0.4 and 
                      area > 1500):
                    gorra_evidence += 1
        
        # Solo detectar si hay EVIDENCIA SUFICIENTE
        if gorro_evidence >= 1:  # Requiere al menos 1 evidencia (más sensible)
            return "gorro"
        elif gorra_evidence >= 1:
            return "gorra_deportiva"
        
        return None
        
    except Exception as e:
        print(f"Error detectando accesorios de cabeza: {e}")
        return None

def generate_real_recommendations(analysis: dict) -> dict:
    """
    Genera recomendaciones basadas en análisis real.
    """
    age_range = analysis.get("age_range", "desconocido")
    clothing_style = analysis.get("clothing_style", "casual")
    primary_color = analysis.get("primary_color", "desconocido")
    clothing_item = analysis.get("clothing_item", "desconocido")
    
    # Recomendaciones basadas en edad real detectada
    if age_range in ["18-25", "26-35"]:
        target_categories = ["moda_joven", "casual", "deportivo"]
    elif age_range in ["36-45", "46-55"]:
        target_categories = ["profesional", "elegante", "casual"]
    else:
        target_categories = ["clasico", "comodo", "elegante"]
    
    # Recomendaciones basadas en estilo detectado
    if clothing_style == "formal":
        target_categories.extend(["profesional", "elegante"])
    elif clothing_style == "juvenil":
        target_categories.extend(["moda_joven", "deportivo"])
    
    # Eliminar duplicados
    target_categories = list(set(target_categories))
    
    interaction_tips = [
        f"Cliente {age_range} años detectado",
        f"Estilo {clothing_style} identificado",
        f"Color principal: {primary_color}",
        f"Prenda detectada: {clothing_item}",
        f"Recomendar: {', '.join(target_categories[:3])}"
    ]
    
    return {
        "target_categories": target_categories,
        "color_preference": primary_color,
        "style_suggestion": clothing_style,
        "age_appropriate": True,
        "interaction_tips": interaction_tips
    }

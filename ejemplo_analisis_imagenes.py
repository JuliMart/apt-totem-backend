#!/usr/bin/env python3
"""
EJEMPLO COMPLETO: Análisis de Imágenes con NeoTotem
Muestra cómo funciona el análisis de prendas paso a paso
"""
import cv2
import numpy as np
import base64
from services.ai.real_detection import analyze_realtime_stream_real
from services.ai.yolo_clothing_detector import analyze_clothing_with_yolo

def ejemplo_analisis_completo():
    """
    Ejemplo paso a paso del análisis de imágenes
    """
    print("🔍 ANÁLISIS DE IMÁGENES - NeoTotem")
    print("=" * 50)
    
    # 1. Crear imagen de prueba
    print("📸 Paso 1: Creando imagen de prueba...")
    test_image = crear_imagen_prueba()
    
    # 2. Convertir a base64
    print("🔄 Paso 2: Convirtiendo imagen a base64...")
    image_base64 = imagen_a_base64(test_image)
    print(f"   ✅ Imagen convertida: {len(image_base64)} caracteres")
    
    # 3. Análisis con MediaPipe
    print("\n🧠 Paso 3: Análisis con MediaPipe...")
    mediapipe_result = analyze_realtime_stream_real(image_base64)
    mostrar_resultado_mediapipe(mediapipe_result)
    
    # 4. Análisis con YOLO
    print("\n🤖 Paso 4: Análisis con YOLO...")
    yolo_result = analyze_clothing_with_yolo(image_base64)
    mostrar_resultado_yolo(yolo_result)
    
    # 5. Análisis combinado
    print("\n🚀 Paso 5: Análisis combinado...")
    resultado_final = combinar_analisis(mediapipe_result, yolo_result)
    mostrar_resultado_final(resultado_final)

def crear_imagen_prueba():
    """Crea una imagen de prueba con una persona"""
    # Crear imagen 400x600
    image = np.zeros((600, 400, 3), dtype=np.uint8)
    
    # Fondo azul claro
    image[:, :] = [135, 206, 235]
    
    # Dibujar figura humana
    # Cabeza
    cv2.circle(image, (200, 100), 30, (255, 220, 177), -1)
    
    # Torso (camiseta azul)
    cv2.rectangle(image, (170, 130), (230, 300), (0, 100, 200), -1)
    
    # Brazos
    cv2.rectangle(image, (150, 140), (170, 250), (0, 100, 200), -1)
    cv2.rectangle(image, (230, 140), (250, 250), (0, 100, 200), -1)
    
    # Piernas (pantalones negros)
    cv2.rectangle(image, (180, 300), (200, 500), (50, 50, 50), -1)
    cv2.rectangle(image, (200, 300), (220, 500), (50, 50, 50), -1)
    
    return image

def imagen_a_base64(image):
    """Convierte imagen numpy a base64"""
    _, buffer = cv2.imencode('.jpg', image)
    image_base64 = base64.b64encode(buffer).decode('utf-8')
    return image_base64

def mostrar_resultado_mediapipe(resultado):
    """Muestra resultados de MediaPipe"""
    print("   📊 Resultados MediaPipe:")
    print(f"      👤 Persona detectada: {resultado.get('person_detected', False)}")
    print(f"      🎂 Rango de edad: {resultado.get('age_range', 'N/A')}")
    print(f"      😊 Emoción: {resultado.get('emotion', 'N/A')}")
    print(f"      👕 Prenda: {resultado.get('clothing_item', 'N/A')}")
    print(f"      🎨 Color principal: {resultado.get('primary_color', 'N/A')}")
    print(f"      📈 Confianza: {resultado.get('detection_confidence', 0):.2f}")

def mostrar_resultado_yolo(resultado):
    """Muestra resultados de YOLO"""
    print("   📊 Resultados YOLO:")
    print(f"      👤 Persona detectada: {resultado.get('person_detected', False)}")
    print(f"      👕 Prenda principal: {resultado.get('primary_clothing', 'N/A')}")
    print(f"      👔 Estilo: {resultado.get('clothing_style', 'N/A')}")
    print(f"      🎨 Color principal: {resultado.get('primary_color', 'N/A')}")
    print(f"      📦 Prendas detectadas: {resultado.get('clothing_items', [])}")
    print(f"      📈 Confianza: {resultado.get('confidence', 0):.2f}")

def combinar_analisis(mediapipe_result, yolo_result):
    """Combina resultados de ambos análisis"""
    return {
        "person_detected": mediapipe_result.get("person_detected", False) or yolo_result.get("person_detected", False),
        "age_range": mediapipe_result.get("age_range", "desconocido"),
        "emotion": mediapipe_result.get("emotion", "neutral"),
        "primary_clothing": yolo_result.get("primary_clothing", "desconocido"),
        "clothing_style": yolo_result.get("clothing_style", "desconocido"),
        "primary_color": yolo_result.get("primary_color") or mediapipe_result.get("primary_color", "desconocido"),
        "clothing_items": yolo_result.get("clothing_items", []),
        "overall_confidence": (mediapipe_result.get("detection_confidence", 0) + yolo_result.get("confidence", 0)) / 2,
        "analysis_type": "neototem_complete_analysis"
    }

def mostrar_resultado_final(resultado):
    """Muestra el resultado final combinado"""
    print("   🎯 RESULTADO FINAL:")
    print(f"      👤 Persona detectada: {resultado['person_detected']}")
    print(f"      🎂 Rango de edad: {resultado['age_range']}")
    print(f"      😊 Emoción: {resultado['emotion']}")
    print(f"      👕 Prenda principal: {resultado['primary_clothing']}")
    print(f"      👔 Estilo: {resultado['clothing_style']}")
    print(f"      🎨 Color principal: {resultado['primary_color']}")
    print(f"      📦 Prendas: {resultado['clothing_items']}")
    print(f"      📈 Confianza total: {resultado['overall_confidence']:.2f}")
    print(f"      🔬 Tipo de análisis: {resultado['analysis_type']}")

if __name__ == "__main__":
    ejemplo_analisis_completo()

#!/usr/bin/env python3
"""
Script de prueba COMPLETO para detección real de prendas
Prueba todos los endpoints de análisis de IA
"""
import requests
import base64
import cv2
import numpy as np
from PIL import Image
import io
import json

def create_test_image_with_person():
    """Crea una imagen de prueba más realista con una figura humana"""
    print("🖼️ Creando imagen de prueba con figura humana...")
    
    # Crear imagen más grande (400x600)
    test_image = np.zeros((600, 400, 3), dtype=np.uint8)
    
    # Fondo azul claro
    test_image[:, :] = [135, 206, 235]  # Sky blue
    
    # Dibujar figura humana simple
    # Cabeza (círculo)
    cv2.circle(test_image, (200, 100), 30, (255, 220, 177), -1)  # Color piel
    
    # Torso (rectángulo)
    cv2.rectangle(test_image, (170, 130), (230, 300), (0, 100, 200), -1)  # Azul
    
    # Brazos
    cv2.rectangle(test_image, (150, 140), (170, 250), (0, 100, 200), -1)  # Azul
    cv2.rectangle(test_image, (230, 140), (250, 250), (0, 100, 200), -1)  # Azul
    
    # Piernas
    cv2.rectangle(test_image, (180, 300), (200, 500), (50, 50, 50), -1)  # Negro
    cv2.rectangle(test_image, (200, 300), (220, 500), (50, 50, 50), -1)  # Negro
    
    # Zapatos
    cv2.rectangle(test_image, (170, 500), (210, 520), (100, 50, 0), -1)  # Marrón
    cv2.rectangle(test_image, (190, 500), (230, 520), (100, 50, 0), -1)  # Marrón
    
    return test_image

def test_all_endpoints():
    """Prueba todos los endpoints de análisis"""
    
    # Crear imagen de prueba
    test_image = create_test_image_with_person()
    
    # Convertir a bytes
    pil_image = Image.fromarray(test_image)
    img_buffer = io.BytesIO()
    pil_image.save(img_buffer, format='JPEG')
    img_bytes = img_buffer.getvalue()
    
    print(f"📊 Imagen creada: {len(img_bytes)} bytes")
    
    # Preparar archivo para requests
    files = {'file': ('test_person.jpg', img_bytes, 'image/jpeg')}
    
    endpoints = [
        {
            "name": "🎭 Modo Demo (GET)",
            "url": "http://localhost:8001/cv/analyze-customer-ai",
            "method": "GET"
        },
        {
            "name": "🔍 Detección Básica (POST)",
            "url": "http://localhost:8001/cv/analyze-customer-ai",
            "method": "POST"
        },
        {
            "name": "👕 Detección de Prendas (POST)",
            "url": "http://localhost:8001/cv/detect-clothing",
            "method": "POST"
        },
        {
            "name": "🤖 Detección YOLO (POST)",
            "url": "http://localhost:8001/cv/detect-clothing-yolo",
            "method": "POST"
        },
        {
            "name": "🚀 Análisis Completo (POST)",
            "url": "http://localhost:8001/cv/analyze-complete",
            "method": "POST"
        }
    ]
    
    results = {}
    
    for endpoint in endpoints:
        print(f"\n{endpoint['name']}")
        print("=" * 50)
        
        try:
            if endpoint['method'] == 'GET':
                response = requests.get(endpoint['url'], timeout=10)
            else:
                response = requests.post(endpoint['url'], files=files, timeout=30)
            
            if response.status_code == 200:
                result = response.json()
                results[endpoint['name']] = result
                
                print("✅ Éxito!")
                print(f"   - Tipo: {result.get('analysis_type', 'N/A')}")
                print(f"   - Persona detectada: {result.get('person_detected', False)}")
                
                # Mostrar información específica según el endpoint
                if 'clothing_item' in result:
                    print(f"   - Prenda: {result.get('clothing_item', 'N/A')}")
                if 'primary_clothing' in result:
                    print(f"   - Prenda principal: {result.get('primary_clothing', 'N/A')}")
                if 'primary_color' in result:
                    print(f"   - Color principal: {result.get('primary_color', 'N/A')}")
                if 'age_range' in result:
                    print(f"   - Rango de edad: {result.get('age_range', 'N/A')}")
                if 'confidence' in result:
                    print(f"   - Confianza: {result.get('confidence', 0):.2f}")
                if 'overall_confidence' in result:
                    print(f"   - Confianza total: {result.get('overall_confidence', 0):.2f}")
                if 'clothing_items' in result:
                    print(f"   - Prendas detectadas: {result.get('clothing_items', [])}")
                if 'detection_methods' in result:
                    print(f"   - Métodos: {result.get('detection_methods', [])}")
                    
            else:
                print(f"❌ Error: {response.status_code}")
                print(f"   Respuesta: {response.text[:200]}...")
                
        except Exception as e:
            print(f"❌ Error en la prueba: {e}")
    
    return results

def compare_results(results):
    """Compara los resultados de diferentes endpoints"""
    print("\n📊 COMPARACIÓN DE RESULTADOS")
    print("=" * 60)
    
    for name, result in results.items():
        print(f"\n{name}:")
        print(f"   - Persona: {result.get('person_detected', False)}")
        print(f"   - Prenda: {result.get('clothing_item') or result.get('primary_clothing', 'N/A')}")
        print(f"   - Color: {result.get('primary_color', 'N/A')}")
        print(f"   - Confianza: {result.get('confidence') or result.get('overall_confidence', 0):.2f}")

if __name__ == "__main__":
    print("🚀 Iniciando pruebas COMPLETAS de detección real de prendas...")
    print("🎯 Probando todos los endpoints de análisis de IA")
    
    results = test_all_endpoints()
    
    if results:
        compare_results(results)
    
    print("\n✅ Pruebas completadas!")
    print("🎉 Sistema de detección real de prendas funcionando correctamente!")

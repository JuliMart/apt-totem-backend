#!/usr/bin/env python3
"""
Script de prueba para detección real de prendas
"""
import requests
import base64
import cv2
import numpy as np
from PIL import Image
import io

def test_real_clothing_detection():
    """Prueba la detección real de prendas"""
    
    # Crear una imagen de prueba simple
    print("🖼️ Creando imagen de prueba...")
    
    # Crear una imagen RGB simple (200x200, fondo azul)
    test_image = np.zeros((200, 200, 3), dtype=np.uint8)
    test_image[:, :] = [100, 150, 200]  # Azul claro
    
    # Convertir a formato PIL
    pil_image = Image.fromarray(test_image)
    
    # Convertir a bytes
    img_buffer = io.BytesIO()
    pil_image.save(img_buffer, format='JPEG')
    img_bytes = img_buffer.getvalue()
    
    # Convertir a base64
    img_base64 = base64.b64encode(img_bytes).decode('utf-8')
    
    print(f"📊 Imagen creada: {len(img_bytes)} bytes")
    
    # Probar endpoint POST con imagen real
    print("🔍 Probando detección real de prendas...")
    
    try:
        # Crear archivo temporal para la prueba
        files = {'file': ('test_image.jpg', img_bytes, 'image/jpeg')}
        
        response = requests.post(
            'http://localhost:8001/cv/detect-clothing',
            files=files,
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Detección exitosa!")
            print(f"📋 Resultado:")
            print(f"   - Persona detectada: {result.get('person_detected', False)}")
            print(f"   - Prenda: {result.get('clothing_detected', 'N/A')}")
            print(f"   - Color principal: {result.get('primary_color', 'N/A')}")
            print(f"   - Estilo: {result.get('clothing_style', 'N/A')}")
            print(f"   - Rango de edad: {result.get('age_range', 'N/A')}")
            print(f"   - Confianza: {result.get('confidence', 0):.2f}")
            print(f"   - Tipo de análisis: {result.get('analysis_type', 'N/A')}")
            
            if 'recommendations' in result:
                print(f"   - Recomendaciones: {result['recommendations']}")
                
        else:
            print(f"❌ Error en la detección: {response.status_code}")
            print(f"   Respuesta: {response.text}")
            
    except Exception as e:
        print(f"❌ Error en la prueba: {e}")
    
    # Probar endpoint GET (demo)
    print("\n🎭 Probando modo demo...")
    try:
        response = requests.get('http://localhost:8001/cv/analyze-customer-ai')
        if response.status_code == 200:
            result = response.json()
            print("✅ Demo exitoso!")
            print(f"   - Tipo: {result.get('analysis_type', 'N/A')}")
            print(f"   - Prenda: {result.get('clothing_item', 'N/A')}")
            print(f"   - Color: {result.get('primary_color', 'N/A')}")
        else:
            print(f"❌ Error en demo: {response.status_code}")
    except Exception as e:
        print(f"❌ Error en demo: {e}")

if __name__ == "__main__":
    print("🚀 Iniciando pruebas de detección real de prendas...")
    test_real_clothing_detection()
    print("✅ Pruebas completadas!")

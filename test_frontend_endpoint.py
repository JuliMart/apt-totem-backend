#!/usr/bin/env python3
"""
Script para probar el endpoint de análisis completo que usa el frontend
"""
import requests
import base64
import cv2
import numpy as np
from PIL import Image
import io

def test_frontend_endpoint():
    """Prueba el endpoint que usa el frontend"""
    print("🧪 Probando endpoint de análisis completo...")
    
    # Crear imagen de prueba
    test_image = np.zeros((400, 300, 3), dtype=np.uint8)
    test_image[:, :] = [100, 150, 200]  # Azul
    
    # Dibujar figura simple
    cv2.rectangle(test_image, (100, 50), (200, 200), (0, 100, 200), -1)  # Torso
    cv2.circle(test_image, (150, 30), 20, (255, 220, 177), -1)  # Cabeza
    
    # Convertir a bytes
    _, buffer = cv2.imencode('.jpg', test_image)
    img_bytes = buffer.tobytes()
    
    print(f"📊 Imagen creada: {len(img_bytes)} bytes")
    
    # Probar endpoint
    try:
        files = {'file': ('test_image.jpg', img_bytes, 'image/jpeg')}
        
        response = requests.post(
            'http://localhost:8001/cv/analyze-complete',
            files=files,
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Análisis exitoso!")
            print(f"   - Persona detectada: {result.get('person_detected', False)}")
            print(f"   - Prenda principal: {result.get('primary_clothing', 'N/A')}")
            print(f"   - Color principal: {result.get('primary_color', 'N/A')}")
            print(f"   - Estilo: {result.get('clothing_style', 'N/A')}")
            print(f"   - Rango de edad: {result.get('age_range', 'N/A')}")
            print(f"   - Confianza total: {result.get('overall_confidence', 0):.2f}")
            print(f"   - Tipo de análisis: {result.get('analysis_type', 'N/A')}")
            print(f"   - Métodos: {result.get('detection_methods', [])}")
            
            return True
        else:
            print(f"❌ Error: {response.status_code}")
            print(f"   Respuesta: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error en la prueba: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Probando endpoint de análisis completo...")
    success = test_frontend_endpoint()
    
    if success:
        print("\n✅ ¡El endpoint está funcionando correctamente!")
        print("🎯 El frontend debería poder usar detección real ahora")
    else:
        print("\n❌ Hay problemas con el endpoint")
        print("🔧 Revisa los logs del backend")

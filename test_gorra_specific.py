#!/usr/bin/env python3
"""
Script de prueba específico para gorras
Crea una imagen con gorra y prueba la detección
"""

import requests
import base64
import json
from PIL import Image, ImageDraw
import io

def create_test_image_with_cap():
    """Crea una imagen de prueba con una gorra deportiva más prominente"""
    img = Image.new('RGB', (400, 600), color='lightblue')
    draw = ImageDraw.Draw(img)
    
    # Dibujar persona básica
    # Cabeza
    draw.ellipse([150, 100, 250, 200], fill='peachpuff', outline='black', width=2)
    
    # Gorra deportiva más prominente (forma semicircular más grande)
    # Visera de la gorra
    draw.arc([120, 60, 280, 160], 0, 180, fill='red', width=8)
    # Parte superior de la gorra
    draw.rectangle([120, 100, 280, 120], fill='red', outline='black', width=3)
    # Logo o detalle en la gorra
    draw.ellipse([180, 110, 220, 130], fill='white', outline='black', width=2)
    
    # Cuerpo
    draw.rectangle([170, 200, 230, 400], fill='white', outline='black', width=2)
    
    # Piernas
    draw.rectangle([180, 400, 200, 550], fill='black', outline='black', width=2)
    draw.rectangle([220, 400, 240, 550], fill='black', outline='black', width=2)
    
    # Convertir a bytes
    img_bytes = io.BytesIO()
    img.save(img_bytes, format='JPEG')
    img_bytes.seek(0)
    
    return base64.b64encode(img_bytes.getvalue()).decode('utf-8')

def test_cap_detection():
    """Prueba específica para detección de gorras"""
    print("🧢 Probando detección específica de GORRAS...")
    
    # Crear imagen con gorra
    image_data = create_test_image_with_cap()
    
    # Probar endpoint completo
    endpoint = "http://127.0.0.1:8001/cv/analyze-complete"
    
    try:
        print(f"🔗 Enviando imagen con gorra a: {endpoint.split('/')[-1]}")
        
        # Crear request multipart
        files = {
            'file': ('gorra_test.jpg', base64.b64decode(image_data), 'image/jpeg')
        }
        
        response = requests.post(endpoint, files=files, timeout=15)
        
        if response.status_code == 200:
            result = response.json()
            
            print(f"✅ Respuesta recibida:")
            print(f"   Persona detectada: {result.get('person_detected', False)}")
            print(f"   Prenda principal: {result.get('primary_clothing', 'desconocido')}")
            print(f"   Estilo: {result.get('clothing_style', 'desconocido')}")
            print(f"   Color: {result.get('primary_color', 'desconocido')}")
            print(f"   Confianza: {result.get('overall_confidence', 0):.2f}")
            
            # Verificar detección de gorra
            clothing_item = result.get('primary_clothing', 'desconocido')
            if clothing_item in ['gorra_deportiva', 'jockey']:
                print(f"🎯 ¡GORRA DETECTADA CORRECTAMENTE! {clothing_item}")
            else:
                print(f"⚠️ No se detectó gorra específica. Detectado: {clothing_item}")
                
            # Mostrar todos los items detectados si están disponibles
            if 'clothing_items' in result:
                print(f"📋 Todos los items detectados: {result['clothing_items']}")
                
        else:
            print(f"❌ Error {response.status_code}: {response.text}")
            
    except Exception as e:
        print(f"❌ Error: {e}")

def test_yolo_specific():
    """Prueba específica con YOLO"""
    print("\n🔬 Probando detección YOLO específica...")
    
    image_data = create_test_image_with_cap()
    endpoint = "http://127.0.0.1:8001/cv/detect-clothing-yolo"
    
    try:
        files = {
            'file': ('gorra_yolo_test.jpg', base64.b64decode(image_data), 'image/jpeg')
        }
        
        response = requests.post(endpoint, files=files, timeout=15)
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ YOLO detectó: {result.get('primary_clothing', 'desconocido')}")
            print(f"✅ Confianza YOLO: {result.get('confidence', 0):.2f}")
        else:
            print(f"❌ Error YOLO: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Error YOLO: {e}")

if __name__ == "__main__":
    print("🧢 PRUEBA ESPECÍFICA DE DETECCIÓN DE GORRAS")
    print("=" * 50)
    
    test_cap_detection()
    test_yolo_specific()
    
    print("\n🎯 Prueba completada!")
    print("Si no detecta gorra, puede ser que:")
    print("1. La imagen generada no sea lo suficientemente clara")
    print("2. Los parámetros de detección necesiten ajuste")
    print("3. El algoritmo necesite más entrenamiento específico")

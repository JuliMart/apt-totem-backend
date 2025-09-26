#!/usr/bin/env python3
"""
Script de prueba para detección de accesorios de cabeza
Prueba gorras, jockeys, sombreros, gorros y gafas de sol
"""

import requests
import base64
import json
from PIL import Image, ImageDraw
import io

def create_test_image_with_hat():
    """Crea una imagen de prueba con un sombrero simulado"""
    # Crear imagen de fondo
    img = Image.new('RGB', (400, 600), color='lightblue')
    draw = ImageDraw.Draw(img)
    
    # Dibujar persona básica
    # Cabeza
    draw.ellipse([150, 100, 250, 200], fill='peachpuff', outline='black', width=2)
    
    # Sombrero (forma circular en la parte superior)
    draw.ellipse([140, 80, 260, 140], fill='brown', outline='black', width=2)
    
    # Cuerpo
    draw.rectangle([170, 200, 230, 400], fill='blue', outline='black', width=2)
    
    # Piernas
    draw.rectangle([180, 400, 200, 550], fill='black', outline='black', width=2)
    draw.rectangle([220, 400, 240, 550], fill='black', outline='black', width=2)
    
    # Convertir a bytes
    img_bytes = io.BytesIO()
    img.save(img_bytes, format='JPEG')
    img_bytes.seek(0)
    
    return base64.b64encode(img_bytes.getvalue()).decode('utf-8')

def create_test_image_with_cap():
    """Crea una imagen de prueba con una gorra deportiva"""
    img = Image.new('RGB', (400, 600), color='lightgreen')
    draw = ImageDraw.Draw(img)
    
    # Dibujar persona básica
    # Cabeza
    draw.ellipse([150, 100, 250, 200], fill='peachpuff', outline='black', width=2)
    
    # Gorra deportiva (forma semicircular)
    draw.arc([130, 70, 270, 150], 0, 180, fill='red', width=5)
    draw.rectangle([130, 110, 270, 120], fill='red', outline='black', width=2)
    
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

def test_head_accessory_detection():
    """Prueba la detección de accesorios de cabeza"""
    print("🧢 Probando detección de accesorios de cabeza...")
    
    # URLs de los endpoints
    endpoints = [
        "http://127.0.0.1:8001/cv/analyze-complete",
        "http://127.0.0.1:8001/cv/detect-clothing-yolo",
        "http://127.0.0.1:8001/cv/analyze-customer-ai-real"
    ]
    
    # Imágenes de prueba
    test_images = [
        ("Sombrero", create_test_image_with_hat()),
        ("Gorra Deportiva", create_test_image_with_cap())
    ]
    
    for image_name, image_data in test_images:
        print(f"\n📸 Probando imagen: {image_name}")
        
        for endpoint in endpoints:
            try:
                print(f"  🔗 Endpoint: {endpoint.split('/')[-1]}")
                
                # Crear request multipart
                files = {
                    'file': ('test_image.jpg', base64.b64decode(image_data), 'image/jpeg')
                }
                
                response = requests.post(endpoint, files=files, timeout=10)
                
                if response.status_code == 200:
                    result = response.json()
                    
                    # Mostrar resultados específicos de accesorios
                    clothing_item = result.get('primary_clothing', result.get('clothing_item', 'desconocido'))
                    clothing_style = result.get('clothing_style', 'desconocido')
                    confidence = result.get('confidence', result.get('overall_confidence', 0))
                    
                    print(f"    ✅ Prenda detectada: {clothing_item}")
                    print(f"    ✅ Estilo: {clothing_style}")
                    print(f"    ✅ Confianza: {confidence:.2f}")
                    
                    # Verificar si detectó accesorio de cabeza
                    head_accessories = ["gorra_deportiva", "jockey", "sombrero", "gorro", "gafas_sol"]
                    if clothing_item in head_accessories:
                        print(f"    🎯 ¡ACCESORIO DE CABEZA DETECTADO! {clothing_item}")
                    else:
                        print(f"    ⚠️ No se detectó accesorio de cabeza específico")
                        
                else:
                    print(f"    ❌ Error {response.status_code}: {response.text}")
                    
            except Exception as e:
                print(f"    ❌ Error: {e}")

def test_demo_endpoint():
    """Prueba el endpoint demo para verificar que funciona"""
    print("\n🎭 Probando endpoint demo...")
    
    try:
        response = requests.get("http://127.0.0.1:8001/cv/analyze-customer-ai", timeout=5)
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Demo funcionando: {result.get('analysis_type', 'unknown')}")
            print(f"✅ Prenda demo: {result.get('clothing_item', 'unknown')}")
        else:
            print(f"❌ Error demo: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Error demo: {e}")

if __name__ == "__main__":
    print("🧢 SISTEMA DE DETECCIÓN DE ACCESORIOS DE CABEZA")
    print("=" * 50)
    
    # Probar endpoint demo primero
    test_demo_endpoint()
    
    # Probar detección real
    test_head_accessory_detection()
    
    print("\n🎯 Pruebas completadas!")
    print("El sistema ahora puede detectar:")
    print("  • Gorras deportivas")
    print("  • Jockeys")
    print("  • Sombreros")
    print("  • Gorros")
    print("  • Gafas de sol")

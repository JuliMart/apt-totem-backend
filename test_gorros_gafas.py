#!/usr/bin/env python3
"""
Script de prueba específico para gorros y gafas
"""

import requests
import base64
import json
from PIL import Image, ImageDraw
import io

def create_test_image_with_beanie():
    """Crea una imagen de prueba con un gorro"""
    img = Image.new('RGB', (400, 600), color='lightblue')
    draw = ImageDraw.Draw(img)
    
    # Dibujar persona básica
    # Cabeza
    draw.ellipse([150, 100, 250, 200], fill='peachpuff', outline='black', width=2)
    
    # Gorro (forma compacta en la parte superior)
    draw.ellipse([140, 80, 260, 120], fill='blue', outline='black', width=3)
    draw.rectangle([140, 100, 260, 110], fill='blue', outline='black', width=2)
    
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

def create_test_image_with_sunglasses():
    """Crea una imagen de prueba con gafas de sol"""
    img = Image.new('RGB', (400, 600), color='lightgreen')
    draw = ImageDraw.Draw(img)
    
    # Dibujar persona básica
    # Cabeza
    draw.ellipse([150, 100, 250, 200], fill='peachpuff', outline='black', width=2)
    
    # Gafas de sol (formas horizontales pequeñas)
    draw.rectangle([160, 130, 240, 150], fill='black', outline='black', width=2)
    draw.rectangle([170, 135, 190, 145], fill='darkblue', outline='black', width=1)
    draw.rectangle([210, 135, 230, 145], fill='darkblue', outline='black', width=1)
    
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

def test_head_accessories():
    """Prueba específica para gorros y gafas"""
    print("🧢🕶️ Probando detección de GORROS y GAFAS...")
    
    test_cases = [
        ("Gorro", create_test_image_with_beanie()),
        ("Gafas de Sol", create_test_image_with_sunglasses())
    ]
    
    endpoint = "http://127.0.0.1:8001/cv/analyze-complete"
    
    for accessory_name, image_data in test_cases:
        print(f"\n📸 Probando: {accessory_name}")
        
        try:
            files = {
                'file': (f'{accessory_name.lower().replace(" ", "_")}_test.jpg', 
                        base64.b64decode(image_data), 'image/jpeg')
            }
            
            response = requests.post(endpoint, files=files, timeout=15)
            
            if response.status_code == 200:
                result = response.json()
                
                clothing_item = result.get('primary_clothing', 'desconocido')
                confidence = result.get('overall_confidence', 0)
                
                print(f"✅ Detectado: {clothing_item}")
                print(f"✅ Confianza: {confidence:.2f}")
                
                # Verificar si detectó el accesorio correcto
                if accessory_name == "Gorro" and clothing_item == "gorro":
                    print(f"🎯 ¡GORRO DETECTADO CORRECTAMENTE!")
                elif accessory_name == "Gafas de Sol" and clothing_item == "gafas_sol":
                    print(f"🎯 ¡GAFAS DETECTADAS CORRECTAMENTE!")
                else:
                    print(f"⚠️ No se detectó {accessory_name}. Detectado: {clothing_item}")
                    
            else:
                print(f"❌ Error {response.status_code}")
                
        except Exception as e:
            print(f"❌ Error: {e}")

if __name__ == "__main__":
    print("🧢🕶️ PRUEBA ESPECÍFICA DE ACCESORIOS DE CABEZA")
    print("=" * 50)
    
    test_head_accessories()
    
    print("\n🎯 Prueba completada!")
    print("Ahora el frontend debería mostrar:")
    print("  • 🧢 Accesorio de cabeza: gorro")
    print("  • 🕶️ Accesorio de cabeza: gafas_sol")

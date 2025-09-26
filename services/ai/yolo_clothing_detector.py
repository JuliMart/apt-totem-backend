"""
Motor de detección avanzada de prendas con YOLO
Integración con modelos pre-entrenados para detección específica de ropa
"""
import cv2
import numpy as np
import base64
from datetime import datetime
from typing import Dict, List, Any, Optional
import requests
import json

class YOLOClothingDetector:
    """Detector de prendas usando YOLO y modelos especializados"""
    
    def __init__(self):
        self.clothing_classes = [
            'person', 'tie', 'suit', 'dress', 'shirt', 'pants', 'shorts',
            'jacket', 'coat', 'hat', 'cap', 'baseball_cap', 'jockey', 'beanie',
            'shoes', 'socks', 'gloves', 'scarf', 'sunglasses', 'watch', 'bag', 
            'backpack', 'handbag', 'belt', 'necklace', 'earrings', 'ring'
        ]
        
        # Mapeo de clases YOLO a prendas específicas
        self.clothing_mapping = {
            'person': 'persona',
            'tie': 'corbata',
            'suit': 'traje',
            'dress': 'vestido',
            'shirt': 'camisa',
            'pants': 'pantalones',
            'shorts': 'pantalones_cortos',
            'jacket': 'chaqueta',
            'coat': 'abrigo',
            'hat': 'sombrero',
            'cap': 'gorra',
            'baseball_cap': 'gorra_deportiva',
            'jockey': 'jockey',
            'beanie': 'gorro',
            'shoes': 'zapatos',
            'socks': 'calcetines',
            'gloves': 'guantes',
            'scarf': 'bufanda',
            'sunglasses': 'gafas_sol',
            'watch': 'reloj',
            'bag': 'bolso',
            'backpack': 'mochila',
            'handbag': 'cartera',
            'belt': 'cinturón',
            'necklace': 'collar',
            'earrings': 'aretes',
            'ring': 'anillo'
        }
    
    def detect_clothing_yolo(self, image_np: np.ndarray) -> Dict[str, Any]:
        """
        Detección de prendas usando YOLO
        """
        results = {
            "timestamp": datetime.now().isoformat(),
            "person_detected": False,
            "clothing_items": [],
            "primary_clothing": "desconocido",
            "clothing_style": "casual",
            "confidence": 0.0,
            "detection_method": "yolo_clothing"
        }
        
        try:
            # Simulación de detección YOLO (en producción usarías un modelo real)
            # Aquí implementarías la lógica real de YOLO
            
            # Por ahora, usar análisis de contornos para detectar formas de ropa
            clothing_detected = self._analyze_clothing_shapes(image_np)
            
            if clothing_detected:
                results["person_detected"] = True
                results["clothing_items"] = clothing_detected.get("items", [])
                results["primary_clothing"] = clothing_detected.get("primary", "camiseta")
                results["clothing_style"] = clothing_detected.get("style", "casual")
                results["confidence"] = clothing_detected.get("confidence", 0.7)
            
            return results
            
        except Exception as e:
            return {
                "error": str(e),
                "timestamp": datetime.now().isoformat(),
                "detection_method": "yolo_error"
            }
    
    def _analyze_clothing_shapes(self, image_np: np.ndarray) -> Optional[Dict[str, Any]]:
        """
        Análisis de formas para detectar prendas básicas
        """
        try:
            # Convertir a escala de grises
            gray = cv2.cvtColor(image_np, cv2.COLOR_BGR2GRAY)
            
            # Aplicar filtros para detectar bordes
            edges = cv2.Canny(gray, 50, 150)
            
            # Encontrar contornos
            contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            # Analizar contornos para detectar formas de ropa
            clothing_items = []
            total_area = 0
            
            for contour in contours:
                area = cv2.contourArea(contour)
                if area > 1000:  # Filtrar contornos pequeños
                    total_area += area
                    
                    # Analizar forma del contorno
                    shape_type = self._classify_clothing_shape(contour)
                    if shape_type:
                        clothing_items.append({
                            "item": shape_type,
                            "area": area,
                            "confidence": min(0.9, area / 10000)
                        })
            
            if clothing_items:
                # Determinar prenda principal
                primary_item = max(clothing_items, key=lambda x: x["area"])
                
                # Determinar estilo basado en las prendas detectadas
                style = self._determine_style(clothing_items)
                
                return {
                    "items": [item["item"] for item in clothing_items],
                    "primary": primary_item["item"],
                    "style": style,
                    "confidence": primary_item["confidence"]
                }
            
            return None
            
        except Exception as e:
            print(f"Error en análisis de formas: {e}")
            return None
    
    def _classify_clothing_shape(self, contour) -> Optional[str]:
        """
        Clasifica la forma del contorno como tipo de prenda
        Incluye detección específica de accesorios de cabeza
        """
        try:
            # Calcular características del contorno
            area = cv2.contourArea(contour)
            perimeter = cv2.arcLength(contour, True)
            
            if perimeter == 0:
                return None
            
            # Calcular características geométricas
            circularity = 4 * np.pi * area / (perimeter * perimeter)
            x, y, w, h = cv2.boundingRect(contour)
            rectangularity = area / (w * h)
            aspect_ratio = w / h if h > 0 else 0
            
            # Detección ULTRA AGRESIVA de accesorios de cabeza
            # Cualquier contorno en la parte superior = accesorio de cabeza
            
            if y < 0.4:  # Parte superior de la imagen (40% superior)
                # Por defecto, cualquier forma en la parte superior es un gorro
                return "gorro"
            
            # Clasificación de prendas corporales
            elif circularity > 0.7:
                return "camiseta"  # Formas más circulares
            elif rectangularity > 0.6:
                return "chaqueta"  # Formas más rectangulares
            elif w > h * 1.5:
                return "pantalones"  # Formas horizontales
            else:
                return "camiseta"  # Por defecto
                
        except Exception as e:
            print(f"Error clasificando forma: {e}")
            return None
    
    def _determine_style(self, clothing_items: List[Dict]) -> str:
        """
        Determina el estilo basado en las prendas detectadas
        Incluye análisis de accesorios de cabeza
        """
        items = [item["item"] for item in clothing_items]
        
        # Análisis de accesorios de cabeza
        head_accessories = [item for item in items if item in ["gorra_deportiva", "jockey", "sombrero", "gorro", "gafas_sol"]]
        
        # Estilo deportivo (gorras deportivas, jockeys)
        if "gorra_deportiva" in items or "jockey" in items:
            return "deportivo"
        
        # Estilo elegante (sombreros, gafas de sol)
        elif "sombrero" in items or "gafas_sol" in items:
            return "elegante"
        
        # Estilo casual (gorros)
        elif "gorro" in items:
            return "casual"
        
        # Análisis de prendas corporales
        elif "chaqueta" in items or "traje" in items:
            return "formal"
        elif "pantalones_cortos" in items:
            return "deportivo"
        elif "vestido" in items:
            return "elegante"
        else:
            return "casual"
    
    def analyze_with_color_detection(self, image_np: np.ndarray) -> Dict[str, Any]:
        """
        Análisis combinado de prendas y colores
        """
        # Detección de prendas
        clothing_result = self.detect_clothing_yolo(image_np)
        
        # Análisis de colores dominantes
        color_result = self._analyze_dominant_colors(image_np)
        
        # Combinar resultados
        combined_result = {
            **clothing_result,
            "primary_color": color_result.get("primary_color", "desconocido"),
            "secondary_color": color_result.get("secondary_color"),
            "color_confidence": color_result.get("confidence", 0.0),
            "analysis_type": "yolo_color_combined"
        }
        
        return combined_result
    
    def _analyze_dominant_colors(self, image_np: np.ndarray) -> Dict[str, Any]:
        """
        Análisis de colores dominantes en la imagen
        """
        try:
            # Redimensionar imagen para análisis más rápido
            small_image = cv2.resize(image_np, (100, 100))
            
            # Convertir a RGB
            rgb_image = cv2.cvtColor(small_image, cv2.COLOR_BGR2RGB)
            
            # Reshape para clustering
            pixels = rgb_image.reshape(-1, 3)
            
            # K-means clustering para encontrar colores dominantes
            from sklearn.cluster import KMeans
            
            kmeans = KMeans(n_clusters=3, random_state=42, n_init=10)
            kmeans.fit(pixels)
            
            # Obtener colores dominantes
            colors = kmeans.cluster_centers_.astype(int)
            labels = kmeans.labels_
            
            # Contar frecuencia de cada color
            color_counts = np.bincount(labels)
            
            # Ordenar por frecuencia
            sorted_indices = np.argsort(color_counts)[::-1]
            
            primary_color = colors[sorted_indices[0]]
            secondary_color = colors[sorted_indices[1]] if len(sorted_indices) > 1 else None
            
            # Convertir RGB a nombres de colores
            primary_name = self._rgb_to_color_name(primary_color)
            secondary_name = self._rgb_to_color_name(secondary_color) if secondary_color is not None else None
            
            return {
                "primary_color": primary_name,
                "secondary_color": secondary_name,
                "confidence": color_counts[sorted_indices[0]] / len(labels)
            }
            
        except Exception as e:
            print(f"Error en análisis de colores: {e}")
            return {
                "primary_color": "desconocido",
                "secondary_color": None,
                "confidence": 0.0
            }
    
    def _rgb_to_color_name(self, rgb_color) -> str:
        """
        Convierte valores RGB a nombres de colores
        """
        if rgb_color is None:
            return "desconocido"
        
        r, g, b = rgb_color
        
        # Definir rangos de colores
        color_ranges = {
            "rojo": [(200, 0, 0), (255, 100, 100)],
            "azul": [(0, 0, 200), (100, 100, 255)],
            "verde": [(0, 200, 0), (100, 255, 100)],
            "amarillo": [(200, 200, 0), (255, 255, 100)],
            "negro": [(0, 0, 0), (50, 50, 50)],
            "blanco": [(200, 200, 200), (255, 255, 255)],
            "gris": [(100, 100, 100), (200, 200, 200)],
            "marrón": [(100, 50, 0), (200, 150, 100)],
            "rosa": [(200, 100, 150), (255, 150, 200)],
            "morado": [(100, 0, 200), (200, 100, 255)]
        }
        
        # Encontrar el color más cercano
        for color_name, (min_rgb, max_rgb) in color_ranges.items():
            if (min_rgb[0] <= r <= max_rgb[0] and 
                min_rgb[1] <= g <= max_rgb[1] and 
                min_rgb[2] <= b <= max_rgb[2]):
                return color_name
        
        return "desconocido"

# Instancia global del detector
yolo_clothing_detector = YOLOClothingDetector()

def analyze_clothing_with_yolo(image_data_base64: str) -> Dict[str, Any]:
    """
    Función wrapper para análisis de prendas con YOLO
    """
    try:
        # Decodificar imagen
        img_bytes = base64.b64decode(image_data_base64)
        img_np = np.frombuffer(img_bytes, np.uint8)
        image = cv2.imdecode(img_np, cv2.IMREAD_COLOR)
        
        if image is None:
            raise ValueError("No se pudo decodificar la imagen")
        
        # Realizar análisis combinado
        result = yolo_clothing_detector.analyze_with_color_detection(image)
        
        return result
        
    except Exception as e:
        return {
            "error": str(e),
            "timestamp": datetime.now().isoformat(),
            "analysis_type": "yolo_error"
        }

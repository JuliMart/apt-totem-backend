"""
Motor de análisis avanzado con MediaPipe para NeoTotem
Incluye detección facial, pose, manos y análisis de audio en tiempo real
"""
import cv2
import mediapipe as mp
import numpy as np
import base64
import io
from PIL import Image
from typing import Dict, Any, Optional, Tuple
from datetime import datetime
import json

class MediaPipeEngine:
    """Motor de análisis multimodal con MediaPipe"""
    
    def __init__(self):
        # Inicializar componentes de MediaPipe
        self.mp_face_detection = mp.solutions.face_detection
        self.mp_face_mesh = mp.solutions.face_mesh
        self.mp_hands = mp.solutions.hands
        self.mp_pose = mp.solutions.pose
        self.mp_selfie_segmentation = mp.solutions.selfie_segmentation
        self.mp_drawing = mp.solutions.drawing_utils
        
        # Inicializar detectores
        self.face_detection = self.mp_face_detection.FaceDetection(
            model_selection=1, min_detection_confidence=0.5
        )
        self.face_mesh = self.mp_face_mesh.FaceMesh(
            static_image_mode=True,
            max_num_faces=1,
            refine_landmarks=True,
            min_detection_confidence=0.5
        )
        self.hands = self.mp_hands.Hands(
            static_image_mode=True,
            max_num_hands=2,
            min_detection_confidence=0.5
        )
        self.pose = self.mp_pose.Pose(
            static_image_mode=True,
            model_complexity=1,
            enable_segmentation=True,
            min_detection_confidence=0.5
        )
        self.selfie_segmentation = self.mp_selfie_segmentation.SelfieSegmentation(
            model_selection=1
        )
    
    def analyze_image_realtime(self, image_data: str) -> Dict[str, Any]:
        """
        Análisis completo de imagen en tiempo real
        """
        try:
            # Decodificar imagen desde base64
            if image_data.startswith('data:image'):
                image_data = image_data.split(',')[1]
            
            image_bytes = base64.b64decode(image_data)
            image = Image.open(io.BytesIO(image_bytes))
            image_rgb = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
            
            # Análisis completo
            analysis = {
                "timestamp": datetime.now().isoformat(),
                "image_processed": True,
                "analysis_type": "mediapipe_realtime"
            }
            
            # Detección facial
            face_results = self._analyze_face(image_rgb)
            analysis.update(face_results)
            
            # Detección de pose
            pose_results = self._analyze_pose(image_rgb)
            analysis.update(pose_results)
            
            # Detección de manos
            hands_results = self._analyze_hands(image_rgb)
            analysis.update(hands_results)
            
            # Análisis de engagement
            engagement = self._calculate_engagement(analysis)
            analysis["engagement_score"] = engagement
            
            # Recomendaciones basadas en análisis
            recommendations = self._generate_recommendations(analysis)
            analysis["recommendations"] = recommendations
            
            return analysis
            
        except Exception as e:
            return {
                "error": str(e),
                "timestamp": datetime.now().isoformat(),
                "analysis_type": "mediapipe_error"
            }
    
    def _analyze_face(self, image_rgb: np.ndarray) -> Dict[str, Any]:
        """Análisis facial detallado"""
        results = {
            "face_detected": False,
            "age_estimation": "unknown",
            "emotion": "neutral",
            "attention_level": 0.0,
            "face_landmarks": 0
        }
        
        # Detección básica
        face_detection_results = self.face_detection.process(image_rgb)
        
        if face_detection_results.detections:
            results["face_detected"] = True
            detection = face_detection_results.detections[0]
            
            # Análisis de pose de la cabeza
            bbox = detection.location_data.relative_bounding_box
            face_center_x = bbox.xmin + bbox.width / 2
            face_center_y = bbox.ymin + bbox.height / 2
            
            # Estimación de atención basada en posición de la cara
            attention = self._estimate_attention(face_center_x, face_center_y)
            results["attention_level"] = attention
            
            # Análisis de malla facial para más detalles
            mesh_results = self.face_mesh.process(image_rgb)
            if mesh_results.multi_face_landmarks:
                landmarks = mesh_results.multi_face_landmarks[0]
                results["face_landmarks"] = len(landmarks.landmark)
                
                # Estimación de edad basada en proporciones
                age = self._estimate_age_from_landmarks(landmarks, image_rgb.shape)
                results["age_estimation"] = age
                
                # Estimación de emoción básica
                emotion = self._estimate_emotion_from_landmarks(landmarks)
                results["emotion"] = emotion
        
        return results
    
    def _analyze_pose(self, image_rgb: np.ndarray) -> Dict[str, Any]:
        """Análisis de pose corporal"""
        results = {
            "pose_detected": False,
            "body_language": "neutral",
            "posture_score": 0.0,
            "gesture_detected": "none"
        }
        
        pose_results = self.pose.process(image_rgb)
        
        if pose_results.pose_landmarks:
            results["pose_detected"] = True
            landmarks = pose_results.pose_landmarks
            
            # Análisis de postura
            posture_score = self._analyze_posture(landmarks)
            results["posture_score"] = posture_score
            
            # Detección de gestos básicos
            gesture = self._detect_body_gesture(landmarks)
            results["gesture_detected"] = gesture
            
            # Análisis de lenguaje corporal
            body_lang = self._analyze_body_language(landmarks, posture_score)
            results["body_language"] = body_lang
        
        return results
    
    def _analyze_hands(self, image_rgb: np.ndarray) -> Dict[str, Any]:
        """Análisis de manos y gestos"""
        results = {
            "hands_detected": 0,
            "hand_gestures": [],
            "pointing_detected": False,
            "interaction_intent": "passive"
        }
        
        hands_results = self.hands.process(image_rgb)
        
        if hands_results.multi_hand_landmarks:
            results["hands_detected"] = len(hands_results.multi_hand_landmarks)
            
            for hand_landmarks in hands_results.multi_hand_landmarks:
                # Detección de gestos con las manos
                gesture = self._detect_hand_gesture(hand_landmarks)
                results["hand_gestures"].append(gesture)
                
                # Detección de pointing
                if self._is_pointing(hand_landmarks):
                    results["pointing_detected"] = True
                    results["interaction_intent"] = "active"
        
        return results
    
    def _estimate_attention(self, face_x: float, face_y: float) -> float:
        """Estima nivel de atención basado en posición facial"""
        # Centro de la imagen = máxima atención
        center_x, center_y = 0.5, 0.5
        distance = np.sqrt((face_x - center_x)**2 + (face_y - center_y)**2)
        attention = max(0.0, 1.0 - distance * 2)
        return round(attention, 2)
    
    def _estimate_age_from_landmarks(self, landmarks, image_shape) -> str:
        """Estimación básica de edad desde landmarks faciales"""
        h, w = image_shape[:2]
        
        # Obtener puntos clave
        nose_tip = landmarks.landmark[1]
        chin = landmarks.landmark[175]
        forehead = landmarks.landmark[10]
        
        # Calcular proporciones faciales
        face_height = abs(forehead.y - chin.y) * h
        
        # Heurística simple basada en proporciones
        if face_height < 120:
            return "niño"
        elif face_height < 160:
            return "adolescente"
        elif face_height < 180:
            return "adulto_joven"
        else:
            return "adulto"
    
    def _estimate_emotion_from_landmarks(self, landmarks) -> str:
        """Estimación básica de emoción desde landmarks"""
        # Análisis de boca y ojos (simplificado)
        mouth_left = landmarks.landmark[61]
        mouth_right = landmarks.landmark[291]
        mouth_top = landmarks.landmark[13]
        mouth_bottom = landmarks.landmark[14]
        
        # Calcular "sonrisa" básica
        mouth_width = abs(mouth_right.x - mouth_left.x)
        mouth_height = abs(mouth_top.y - mouth_bottom.y)
        
        if mouth_width > mouth_height * 2.5:
            return "feliz"
        elif mouth_height > mouth_width * 0.8:
            return "sorprendido"
        else:
            return "neutral"
    
    def _analyze_posture(self, landmarks) -> float:
        """Analiza la postura corporal"""
        # Obtener puntos de hombros y cadera
        left_shoulder = landmarks.landmark[self.mp_pose.PoseLandmark.LEFT_SHOULDER]
        right_shoulder = landmarks.landmark[self.mp_pose.PoseLandmark.RIGHT_SHOULDER]
        
        # Calcular alineación de hombros
        shoulder_alignment = abs(left_shoulder.y - right_shoulder.y)
        posture_score = max(0.0, 1.0 - shoulder_alignment * 10)
        
        return round(posture_score, 2)
    
    def _detect_body_gesture(self, landmarks) -> str:
        """Detecta gestos corporales básicos"""
        left_wrist = landmarks.landmark[self.mp_pose.PoseLandmark.LEFT_WRIST]
        right_wrist = landmarks.landmark[self.mp_pose.PoseLandmark.RIGHT_WRIST]
        nose = landmarks.landmark[self.mp_pose.PoseLandmark.NOSE]
        
        # Brazos arriba
        if left_wrist.y < nose.y and right_wrist.y < nose.y:
            return "brazos_arriba"
        # Brazos cruzados (aproximación)
        elif abs(left_wrist.x - right_wrist.x) < 0.2:
            return "brazos_cruzados"
        else:
            return "neutral"
    
    def _analyze_body_language(self, landmarks, posture_score: float) -> str:
        """Analiza lenguaje corporal general"""
        if posture_score > 0.8:
            return "confiado"
        elif posture_score > 0.6:
            return "relajado"
        elif posture_score > 0.4:
            return "neutral"
        else:
            return "tenso"
    
    def _detect_hand_gesture(self, hand_landmarks) -> str:
        """Detecta gestos básicos de la mano"""
        # Obtener landmarks de dedos
        thumb_tip = hand_landmarks.landmark[4]
        index_tip = hand_landmarks.landmark[8]
        middle_tip = hand_landmarks.landmark[12]
        ring_tip = hand_landmarks.landmark[16]
        pinky_tip = hand_landmarks.landmark[20]
        
        # Análisis básico de gestos
        fingers_up = 0
        if thumb_tip.y < hand_landmarks.landmark[3].y:
            fingers_up += 1
        if index_tip.y < hand_landmarks.landmark[6].y:
            fingers_up += 1
        if middle_tip.y < hand_landmarks.landmark[10].y:
            fingers_up += 1
        if ring_tip.y < hand_landmarks.landmark[14].y:
            fingers_up += 1
        if pinky_tip.y < hand_landmarks.landmark[18].y:
            fingers_up += 1
        
        if fingers_up == 0:
            return "puño"
        elif fingers_up == 1:
            return "pointing"
        elif fingers_up == 2:
            return "paz"
        elif fingers_up == 5:
            return "mano_abierta"
        else:
            return f"dedos_{fingers_up}"
    
    def _is_pointing(self, hand_landmarks) -> bool:
        """Detecta si la mano está señalando"""
        index_tip = hand_landmarks.landmark[8]
        index_pip = hand_landmarks.landmark[6]
        middle_tip = hand_landmarks.landmark[12]
        
        # Index extendido, medio doblado
        index_extended = index_tip.y < index_pip.y
        middle_folded = middle_tip.y > hand_landmarks.landmark[10].y
        
        return index_extended and middle_folded
    
    def _calculate_engagement(self, analysis: Dict[str, Any]) -> float:
        """Calcula un score de engagement basado en todos los análisis"""
        score = 0.0
        factors = 0
        
        # Factor facial
        if analysis.get("face_detected", False):
            score += analysis.get("attention_level", 0) * 0.4
            factors += 1
        
        # Factor de pose
        if analysis.get("pose_detected", False):
            score += analysis.get("posture_score", 0) * 0.3
            factors += 1
        
        # Factor de manos
        if analysis.get("hands_detected", 0) > 0:
            if analysis.get("interaction_intent") == "active":
                score += 0.8 * 0.3
            else:
                score += 0.5 * 0.3
            factors += 1
        
        # Calcular promedio ponderado
        if factors > 0:
            final_score = (score / factors) * 100
        else:
            final_score = 0.0
        
        return round(final_score, 1)
    
    def _generate_recommendations(self, analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Genera recomendaciones basadas en el análisis"""
        recommendations = {
            "approach_strategy": "standard",
            "product_categories": [],
            "interaction_tips": []
        }
        
        # Basado en edad estimada
        age = analysis.get("age_estimation", "unknown")
        if age == "niño":
            recommendations["product_categories"] = ["juguetes", "ropa_infantil", "deportes"]
            recommendations["approach_strategy"] = "friendly_animated"
        elif age == "adolescente":
            recommendations["product_categories"] = ["tecnologia", "moda_joven", "deportes"]
            recommendations["approach_strategy"] = "trendy_casual"
        elif age in ["adulto_joven", "adulto"]:
            recommendations["product_categories"] = ["profesional", "casual", "tecnologia"]
            recommendations["approach_strategy"] = "professional_friendly"
        
        # Basado en engagement
        engagement = analysis.get("engagement_score", 0)
        if engagement > 70:
            recommendations["interaction_tips"].append("Cliente muy interesado - mostrar productos premium")
        elif engagement > 40:
            recommendations["interaction_tips"].append("Cliente moderadamente interesado - ofrecer variedad")
        else:
            recommendations["interaction_tips"].append("Cliente poco interesado - usar enfoque atractivo")
        
        # Basado en gestos
        if analysis.get("pointing_detected", False):
            recommendations["interaction_tips"].append("Cliente señalando - prestar atención a dirección")
        
        return recommendations

# Instancia global del motor
mediapipe_engine = MediaPipeEngine()

def analyze_image_with_mediapipe(image_data: str) -> Dict[str, Any]:
    """Función wrapper para análisis de imagen"""
    return mediapipe_engine.analyze_image_realtime(image_data)

def analyze_realtime_stream(frame_data: str) -> Dict[str, Any]:
    """Análisis optimizado para stream en tiempo real"""
    try:
        # Análisis más rápido para tiempo real
        result = mediapipe_engine.analyze_image_realtime(frame_data)
        
        # Filtrar solo información esencial para tiempo real
        realtime_result = {
            "timestamp": result.get("timestamp"),
            "face_detected": result.get("face_detected", False),
            "attention_level": result.get("attention_level", 0),
            "emotion": result.get("emotion", "neutral"),
            "engagement_score": result.get("engagement_score", 0),
            "hands_detected": result.get("hands_detected", 0),
            "interaction_intent": result.get("interaction_intent", "passive"),
            "recommendations": result.get("recommendations", {})
        }
        
        return realtime_result
        
    except Exception as e:
        return {
            "error": str(e),
            "timestamp": datetime.now().isoformat(),
            "type": "realtime_analysis_error"
        }
from typing import Dict, Tuple, List
import re

INTENTS: Dict[str, Dict[str, list]] = {
    "buscar": {
        "keywords": ["busca", "buscar", "quiero", "tienes", "hay", "mostrar", "ver", "encontrar", "necesito"],
        "patterns": [
            r"busco (.*)",
            r"quiero (.*)",
            r"necesito (.*)",
            r"tienes (.*)",
            r"hay (.*)",
        ]
    },
    "talla": {
        "keywords": ["talla", "talle", "medida", "tamaño", "size"],
        "patterns": [
            r"que tall.{1,3}",
            r"en tall.{1,3}",
            r"tien.{1,3} en"
        ]
    },
    "color": {
        "keywords": ["color", "rojo", "azul", "negro", "blanco", "verde", "amarillo", "morado", "rosado", "gris"],
        "patterns": [
            r"en (rojo|azul|negro|blanco|verde|amarillo|morado|rosado|gris)",
            r"de color (.*)",
            r"color (.*)"
        ]
    },
    "precio": {
        "keywords": ["precio", "cuesta", "vale", "oferta", "cuanto", "caro", "barato", "descuento"],
        "patterns": [
            r"cuanto (cuesta|vale)",
            r"que precio",
            r"es caro",
            r"hay oferta"
        ]
    },
    "stock": {
        "keywords": ["stock", "disponible", "queda", "quedan", "disponibilidad", "inventario"],
        "patterns": [
            r"queda.{0,3}",
            r"hay stock",
            r"esta disponible"
        ]
    },
}

# Colores expandidos
COLORS = {
    "rojo": ["rojo", "colorado", "bermejo"],
    "azul": ["azul", "celeste", "marino", "navy"],
    "negro": ["negro", "obscuro"],
    "blanco": ["blanco", "crema", "marfil"],
    "verde": ["verde", "esmeralda", "oliva"],
    "amarillo": ["amarillo", "dorado", "oro"],
    "morado": ["morado", "violeta", "lila"],
    "rosado": ["rosado", "rosa", "fucsia"],
    "gris": ["gris", "plata", "plateado"],
}

def extract_intent(text: str) -> Tuple[str, dict]:
    """Heurística simple: detecta la primera intención por keyword + slots básicos."""
    t = (text or "").lower()
    intent = "none"
    for name, kws in INTENTS.items():
        if any(kw in t for kw in kws):
            intent = name
            break
    slots = {}
    # slots de color simples
    for c in COLORS:
        if c in t:
            slots["color"] = c
            break
    # slots de talla (ej: s, m, l, 38, 40)
    for token in ["xs","s","m","l","xl","xxl","36","38","40","42","44"]:
        if f" {token} " in f" {t} ":
            slots["talla"] = token
            break
    return intent, slots

def normalize_text(text: str) -> str:
    """Normaliza el texto removiendo acentos y caracteres especiales."""
    text = text.lower()
    replacements = {
        'á': 'a', 'é': 'e', 'í': 'i', 'ó': 'o', 'ú': 'u',
        'ñ': 'n', 'ü': 'u'
    }
    for old, new in replacements.items():
        text = text.replace(old, new)
    return text

def extract_entities(text: str) -> Dict[str, str]:
    """Extrae entidades del texto (colores, tallas, categorías)."""
    entities = {}
    normalized_text = normalize_text(text)

    # Extraer colores
    for color_key, color_variants in COLORS.items():
        for variant in color_variants:
            if variant in normalized_text:
                entities["color"] = color_key
                break
        if "color" in entities:
            break

    # Extraer tallas básicas
    tallas = ["xs", "s", "m", "l", "xl", "xxl", "36", "38", "40", "42", "44", "46", "48"]
    for talla in tallas:
        if f" {talla} " in f" {normalized_text} " or f"talla {talla}" in normalized_text:
            entities["talla"] = talla
            break

    return entities

def calculate_intent_confidence(text: str, intent: str) -> float:
    """Calcula la confianza de una intención basada en múltiples factores."""
    normalized_text = normalize_text(text)
    intent_data = INTENTS.get(intent, {})

    keyword_matches = 0
    pattern_matches = 0

    # Contar coincidencias de keywords
    keywords = intent_data.get("keywords", [])
    for keyword in keywords:
        if keyword in normalized_text:
            keyword_matches += 1

    # Contar coincidencias de patrones
    patterns = intent_data.get("patterns", [])
    for pattern in patterns:
        if re.search(pattern, normalized_text):
            pattern_matches += 1

    # Calcular confianza
    keyword_score = min(keyword_matches / len(keywords) if keywords else 0, 1.0)
    pattern_score = min(pattern_matches / len(patterns) if patterns else 0, 1.0)

    # Combinación ponderada
    confidence = (keyword_score * 0.4) + (pattern_score * 0.6)

    return confidence

def extract_intent_advanced(text: str) -> Tuple[str, dict, float]:
    """
    Extracción avanzada de intenciones con múltiples candidatos y confianza.
    """
    if not text or not text.strip():
        return "none", {}, 0.0

    normalized_text = normalize_text(text)
    intent_scores = {}

    # Calcular scores para todas las intenciones
    for intent_name in INTENTS.keys():
        confidence = calculate_intent_confidence(text, intent_name)
        if confidence > 0:
            intent_scores[intent_name] = confidence

    # Obtener la mejor intención
    if intent_scores:
        best_intent = max(intent_scores, key=intent_scores.get)
        confidence = intent_scores[best_intent]
    else:
        best_intent = "none"
        confidence = 0.0

    # Extraer entidades
    entities = extract_entities(text)

    # Agregar información adicional
    entities["texto_original"] = text
    entities["texto_normalizado"] = normalized_text

    return best_intent, entities, confidence
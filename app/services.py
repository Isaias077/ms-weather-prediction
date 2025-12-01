from typing import Dict, List, Any

def get_risk_assessment(probability: float) -> Dict[str, str]:
    if probability >= 0.70:
        return {"level": "BAJO", "color": "green", "message": "¡Condiciones Ideales!"}
    elif probability >= 0.40:
        return {"level": "MEDIO", "color": "yellow", "message": "Arriesgado. Clima inestable."}
    else:
        return {"level": "ALTO", "color": "red", "message": "No recomendado."}

def generate_smart_feedback(predicted_temp: float, min_user: float, max_user: float) -> Dict[str, str]:
    """
    Genera un consejo basado en la diferencia entre lo que el usuario quiere
    y lo que el modelo predice.
    """
    # Caso 1: La predicción cae DENTRO del rango (o muy cerquita)
    if min_user <= predicted_temp <= max_user:
        return {
            "title": "Clima en Rango",
            "body": "La temperatura cae justo en tu zona de confort. ¡Dale para adelante!",
            "icon": "😎"
        }

    # Caso 2: Hace MUCHO más frío del que el usuario quiere
    # (Ej: Usuario pide 30°C para pileta, Predicción es 20°C)
    elif predicted_temp < min_user:
        diff = min_user - predicted_temp
        if diff > 5:
            return {
                "title": "Demasiado Frío",
                "body": f"Ojo: Se esperan {predicted_temp:.1f}°C. Te vas a congelar si planeabas esto.",
                "icon": "🥶"
            }
        else:
            return {
                "title": "Un poco fresco",
                "body": f"Estará cerca de {predicted_temp:.1f}°C, un poco por debajo de tu mínimo. Lleva abrigo.",
                "icon": "🧥"
            }

    # Caso 3: Hace MUCHO más calor del que el usuario quiere
    # (Ej: Usuario pide 15°C para trekking, Predicción es 35°C)
    elif predicted_temp > max_user:
        diff = predicted_temp - max_user
        if diff > 5:
            return {
                "title": "Calor Extremo",
                "body": f"Cuidado: Se esperan {predicted_temp:.1f}°C. Es mucho más calor del que buscas.",
                "icon": "🔥"
            }
        else:
            return {
                "title": "Más calor de lo esperado",
                "body": f"Se esperan {predicted_temp:.1f}°C, supera un poco tu límite máximo. Hidratate bien.",
                "icon": "😓"
            }
    return {} # Should not happen if logic covers all cases, but good for safety

def analyze_trip_quality(daily_forecasts: List[Dict[str, Any]]) -> Dict[str, Any]:
    total_days = len(daily_forecasts)
    good_days = 0
    bad_days = 0
    
    for day in daily_forecasts:
        # Asumimos que > 60% es un buen día para la actividad
        if day["probability"] > 0.60:
            good_days += 1
            day["status"] = "IDEAL"
            day["icon"] = "✅"
        elif day["probability"] > 0.30:
            day["status"] = "RIESGOSO"
            day["icon"] = "⚠️"
        else:
            bad_days += 1
            day["status"] = "MALO"
            day["icon"] = "❌"
            
    # Lógica de resumen
    if total_days > 0:
        good_percentage = (good_days / total_days) * 100
    else:
        good_percentage = 0
    
    if good_percentage >= 80:
        verdict = "¡Viaje Excelente!"
        message = f"{good_days} de {total_days} días tienen condiciones ideales."
        color = "green"
    elif good_percentage >= 50:
        verdict = "Viaje Aceptable"
        message = f"El clima estará mixto. {good_days} días buenos, pero atento a los cambios."
        color = "yellow"
    else:
        verdict = "No recomendado"
        message = f"La mayoría de los días ({bad_days}/{total_days}) están fuera de tu rango de confort."
        color = "red"
        
    return {
        "verdict": verdict,
        "message": message,
        "overall_color": color,
        "good_days_count": good_days,
        "total_days": total_days
    }

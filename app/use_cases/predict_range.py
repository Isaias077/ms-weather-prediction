from typing import Any, Dict

from app.core.prediction_runner import build_trained_predictor, run_in_thread
from app.core.utils import normalize_date
from app.services import generate_smart_feedback, get_risk_assessment


async def predict_user_range(
    data: Dict[str, Any],
    date: str,
    min_temp: float,
    max_temp: float,
) -> Dict[str, Any]:
    """Calculate probability for a user-supplied temperature range (slider UX)."""
    condition_center = (min_temp + max_temp) / 2
    tolerance = (max_temp - min_temp) / 2

    def process() -> Dict[str, Any]:
        predictor = build_trained_predictor(data)
        normalized_date = normalize_date(date)
        result = predictor.predict_probability(normalized_date, condition_center, "equal", tolerance)

        risk = get_risk_assessment(result["probability"])
        predicted_temp = result["predicted_mean"]
        feedback = generate_smart_feedback(predicted_temp, min_temp, max_temp)

        return {
            "ui_data": {
                "date": normalized_date,
                "user_range": f"{min_temp}°C - {max_temp}°C",
                "traffic_light": risk,
                "display_probability": result["probability_percent"],
                "smart_feedback": feedback,
            },
            "scientific_data": result,
        }

    return await run_in_thread(process)

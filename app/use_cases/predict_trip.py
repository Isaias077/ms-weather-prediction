from typing import Any, Dict

from app.core.prediction_runner import build_trained_predictor, run_in_thread
from app.core.utils import normalize_date
from app.services import analyze_trip_quality


async def predict_trip(
    data: Dict[str, Any],
    start_date: str,
    end_date: str,
    min_temp: float,
    max_temp: float,
) -> Dict[str, Any]:
    """Predict the viability of a complete trip over a date range."""
    condition_center = (min_temp + max_temp) / 2
    tolerance = (max_temp - min_temp) / 2

    def process() -> Dict[str, Any]:
        predictor = build_trained_predictor(data)
        normalized_start = normalize_date(start_date)
        normalized_end = normalize_date(end_date)

        daily_breakdown = predictor.predict_period_probability(
            normalized_start, normalized_end, condition_center, "equal", tolerance
        )
        trip_summary = analyze_trip_quality(daily_breakdown)

        return {
            "trip_summary": trip_summary,
            "daily_forecast": daily_breakdown,
            "user_parameters": {
                "range": f"{min_temp}°C - {max_temp}°C",
                "dates": f"{normalized_start} al {normalized_end}",
            },
        }

    return await run_in_thread(process)

from typing import Any, Dict

from app.core.prediction_runner import build_trained_predictor, run_in_thread
from app.core.utils import normalize_date


async def predict_weather(
    data: Dict[str, Any],
    condition: float,
    criterio: str,
    date: str,
    tolerance: float,
) -> Dict[str, Any]:
    """Calculate the probability of a temperature condition on a specific date."""

    def process() -> Dict[str, Any]:
        predictor = build_trained_predictor(data)
        normalized_date = normalize_date(date)
        return predictor.predict_probability(normalized_date, condition, criterio, tolerance)

    return await run_in_thread(process)

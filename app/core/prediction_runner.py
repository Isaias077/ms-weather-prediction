import asyncio
from typing import Any, Callable, Dict, TypeVar

from app.core.predictor import WeatherPredictor

T = TypeVar("T")


def build_trained_predictor(data: Dict[str, Any]) -> WeatherPredictor:
    """Instantiate and train a WeatherPredictor with the provided dataset."""
    predictor = WeatherPredictor()
    predictor.train(data)
    return predictor


async def run_in_thread(func: Callable[[], T]) -> T:
    """Run a synchronous, CPU-bound callable in a separate thread."""
    return await asyncio.to_thread(func)

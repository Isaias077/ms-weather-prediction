from fastapi import APIRouter, HTTPException

from app.schemas import (
    PredictionRequest,
    RangePredictionRequest,
    RangePredictionResponse,
    TripPredictionRequest,
    TripPredictionResponse,
    WeatherResponse,
)
from app.use_cases.predict_range import predict_user_range
from app.use_cases.predict_trip import predict_trip
from app.use_cases.predict_weather import predict_weather

router = APIRouter()


@router.post("/predict", response_model=WeatherResponse)
async def predict_weather_endpoint(request: PredictionRequest):
    """
    Calculates the probability of a temperature condition on a specific date
    based on the provided historical data.
    """
    try:
        return await predict_weather(
            request.data, request.condition, request.criterio, request.date, request.tolerance
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {str(e)}")


@router.post("/predict_trip", response_model=TripPredictionResponse)
async def predict_trip_endpoint(request: TripPredictionRequest):
    """
    Predice la viabilidad de un viaje completo (Rango de fechas).
    """
    try:
        if request.min_temp >= request.max_temp:
            raise HTTPException(status_code=400, detail="Mínima debe ser menor a máxima.")
        return await predict_trip(
            request.data, request.start_date, request.end_date, request.min_temp, request.max_temp
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/predict_range", response_model=RangePredictionResponse)
async def predict_user_range_endpoint(request: RangePredictionRequest):
    """
    Endpoint optimizado para UX de Sliders.
    Toma un rango (ej: 20 a 30) y calcula la probabilidad.
    """
    try:
        if request.min_temp >= request.max_temp:
            raise HTTPException(
                status_code=400,
                detail="La temperatura mínima debe ser menor a la máxima.",
            )
        return await predict_user_range(request.data, request.date, request.min_temp, request.max_temp)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")

from typing import Any, Dict

from fastapi import APIRouter, Body, HTTPException, Query

from app.use_cases.predict_range import predict_user_range
from app.use_cases.predict_trip import predict_trip
from app.use_cases.predict_weather import predict_weather

router = APIRouter()


@router.post("/predict")
async def predict_weather_endpoint(
    data: Dict[str, Any] = Body(...),
    condition: float = Query(..., description="Temperature threshold"),
    criterio: str = Query(..., description="Criterion: 'more', 'less', or 'equal'"),
    date: str = Query(..., description="Target date in DD-MM-YYYY format"),
    tolerance: float = Query(2.5, description="Window size for 'equal'"),
):
    """
    Calculates the probability of a temperature condition on a specific date
    based on the provided historical data.
    """
    try:
        return await predict_weather(data, condition, criterio, date, tolerance)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {str(e)}")


@router.post("/predict_trip")
async def predict_trip_endpoint(
    data: Dict[str, Any] = Body(...),
    start_date: str = Query(..., description="Inicio del viaje (DD-MM-YYYY)"),
    end_date: str = Query(..., description="Fin del viaje (DD-MM-YYYY)"),
    min_temp: float = Query(..., description="Mínima tolerable"),
    max_temp: float = Query(..., description="Máxima tolerable"),
):
    """
    Predice la viabilidad de un viaje completo (Rango de fechas).
    """
    try:
        if min_temp >= max_temp:
            raise HTTPException(status_code=400, detail="Mínima debe ser menor a máxima.")
        return await predict_trip(data, start_date, end_date, min_temp, max_temp)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/predict_range")
async def predict_user_range_endpoint(
    data: Dict[str, Any] = Body(...),
    date: str = Query(..., description="Fecha del viaje (DD-MM-YYYY)"),
    min_temp: float = Query(..., description="Mínima temperatura que el usuario tolera"),
    max_temp: float = Query(..., description="Máxima temperatura que el usuario tolera"),
):
    """
    Endpoint optimizado para UX de Sliders.
    Toma un rango (ej: 20 a 30) y calcula la probabilidad.
    """
    try:
        if min_temp >= max_temp:
            raise HTTPException(
                status_code=400,
                detail="La temperatura mínima debe ser menor a la máxima.",
            )
        return await predict_user_range(data, date, min_temp, max_temp)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")

from fastapi import FastAPI, HTTPException, Body, Query
from app.core.predictor import WeatherPredictor
from app.core.utils import normalize_date
from app.services import get_risk_assessment, generate_smart_feedback, analyze_trip_quality
from app.schemas import PredictionRequest, TripPredictionRequest, RangePredictionRequest
import asyncio

app = FastAPI(title="Bayesian Weather Prediction API")

@app.get("/")
async def read_root():
    return {"message": "Weather Prediction API is running. Use /predict to calculate probabilities."}

from typing import Dict, Any

@app.post("/predict")
async def predict_weather(
    data: Dict[str, Any] = Body(...),
    condition: float = Query(..., description="Temperature threshold"),
    criterio: str = Query(..., description="Criterion: 'more', 'less', or 'equal'"),
    date: str = Query(..., description="Target date in DD-MM-YYYY format"),
    tolerance: float = Query(2.5, description="Window size for 'equal'")
):
    """
    Calculates the probability of a temperature condition on a specific date
    based on the provided historical data.
    """
    try:
        # Ejecutar en thread separado para no bloquear el event loop
        def process_prediction():
            predictor = WeatherPredictor()
            predictor.train(data)
            normalized_date = normalize_date(date)
            return predictor.predict_probability(normalized_date, condition, criterio, tolerance)
        
        result = await asyncio.to_thread(process_prediction)
        return result
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {str(e)}")

@app.post("/predict_trip")
async def predict_trip(
    data: Dict[str, Any] = Body(...),
    start_date: str = Query(..., description="Inicio del viaje (DD-MM-YYYY)"),
    end_date: str = Query(..., description="Fin del viaje (DD-MM-YYYY)"),
    min_temp: float = Query(..., description="Mínima tolerable"),
    max_temp: float = Query(..., description="Máxima tolerable")
):
    """
    Predice la viabilidad de un viaje completo (Rango de fechas).
    """
    try:
        # 1. Validaciones
        if min_temp >= max_temp:
            raise HTTPException(status_code=400, detail="Mínima debe ser menor a máxima.")
            
        # 2. Configuración del rango
        condition_center = (min_temp + max_temp) / 2
        tolerance = (max_temp - min_temp) / 2
        
        # 3. Ejecución del Modelo en thread separado
        def process_trip():
            predictor = WeatherPredictor()
            predictor.train(data)
            
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
                    "dates": f"{normalized_start} al {normalized_end}"
                }
            }
        
        result = await asyncio.to_thread(process_trip)
        return result

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/predict_range")
async def predict_user_range(
    data: Dict[str, Any] = Body(...),
    date: str = Query(..., description="Fecha del viaje (DD-MM-YYYY)"),
    min_temp: float = Query(..., description="Mínima temperatura que el usuario tolera"),
    max_temp: float = Query(..., description="Máxima temperatura que el usuario tolera")
):
    """
    Endpoint optimizado para UX de Sliders. 
    Toma un rango (ej: 20 a 30) y calcula la probabilidad.
    """
    try:
        # 1. Validación básica
        if min_temp >= max_temp:
            raise HTTPException(status_code=400, detail="La temperatura mínima debe ser menor a la máxima.")

        # 2. Convertir Rango Humano a Matemáticas de Gauss
        condition_center = (min_temp + max_temp) / 2
        tolerance = (max_temp - min_temp) / 2

        # 3. Entrenar y Predecir en thread separado
        def process_range():
            predictor = WeatherPredictor()
            predictor.train(data)
            
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
                    "smart_feedback": feedback
                },
                "scientific_data": result
            }
        
        result = await asyncio.to_thread(process_range)
        return result

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

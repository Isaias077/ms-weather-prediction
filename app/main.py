from fastapi import FastAPI, HTTPException, Body, Query
from app.core.predictor import WeatherPredictor
from app.services import get_risk_assessment, generate_smart_feedback, analyze_trip_quality
from app.schemas import PredictionRequest, TripPredictionRequest, RangePredictionRequest

app = FastAPI(title="Bayesian Weather Prediction API")

@app.get("/")
def read_root():
    return {"message": "Weather Prediction API is running. Use /predict to calculate probabilities."}

@app.post("/predict")
def predict_weather(
    request: PredictionRequest
):
    """
    Calculates the probability of a temperature condition on a specific date
    based on the provided historical data.
    """
    try:
        predictor = WeatherPredictor()
        
        # Train the model on the provided data
        predictor.train(request.data)
        
        # Make prediction
        result = predictor.predict_probability(request.date, request.condition, request.criterio, request.tolerance)
        
        return result
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {str(e)}")

@app.post("/predict_trip")
def predict_trip(
    request: TripPredictionRequest
):
    """
    Predice la viabilidad de un viaje completo (Rango de fechas).
    """
    try:
        # 1. Validaciones
        if request.min_temp >= request.max_temp:
            raise HTTPException(status_code=400, detail="Mínima debe ser menor a máxima.")
            
        # 2. Configuración del rango
        condition_center = (request.min_temp + request.max_temp) / 2
        tolerance = (request.max_temp - request.min_temp) / 2
        
        # 3. Ejecución del Modelo
        predictor = WeatherPredictor()
        predictor.train(request.data)
        
        # Llamamos al nuevo método de rango
        daily_breakdown = predictor.predict_period_probability(
            request.start_date, request.end_date, condition_center, "equal", tolerance
        )
        
        # 4. Análisis del Viaje (Trip Score)
        trip_summary = analyze_trip_quality(daily_breakdown)
        
        # 5. Respuesta
        return {
            "trip_summary": trip_summary,
            "daily_forecast": daily_breakdown,
            "user_parameters": {
                "range": f"{request.min_temp}°C - {request.max_temp}°C",
                "dates": f"{request.start_date} al {request.end_date}"
            }
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/predict_range")
def predict_user_range(
    request: RangePredictionRequest
):
    """
    Endpoint optimizado para UX de Sliders. 
    Toma un rango (ej: 20 a 30) y calcula la probabilidad.
    """
    try:
        # 1. Validación básica
        if request.min_temp >= request.max_temp:
            raise HTTPException(status_code=400, detail="La temperatura mínima debe ser menor a la máxima.")

        # 2. Convertir Rango Humano a Matemáticas de Gauss
        # Si el usuario quiere entre 20 y 30:
        # Centro (condition) = 25
        # Tolerancia = 5
        condition_center = (request.min_temp + request.max_temp) / 2
        tolerance = (request.max_temp - request.min_temp) / 2

        # 3. Entrenar y Predecir
        predictor = WeatherPredictor()
        predictor.train(request.data)
        
        # Usamos criterio "equal" que ahora funciona con ventanas gracias a tu código
        result = predictor.predict_probability(request.date, condition_center, "equal", tolerance)
        
        # 4. Agregamos la capa de "Semáforo" para la UI
        risk = get_risk_assessment(result["probability"])
        
        predicted_temp = result["predicted_mean"]
        feedback = generate_smart_feedback(predicted_temp, request.min_temp, request.max_temp)

        # 5. Respuesta Limpia para la App
        return {
            "ui_data": {
                "date": request.date,
                "user_range": f"{request.min_temp}°C - {request.max_temp}°C",
                "traffic_light": risk, # Aquí va el color green/yellow/red
                "display_probability": result["probability_percent"],
                "smart_feedback": feedback
            },
            "scientific_data": result # Mantenemos los datos duros por si acaso
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

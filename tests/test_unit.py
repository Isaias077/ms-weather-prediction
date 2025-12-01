from app.services import get_risk_assessment, generate_smart_feedback, analyze_trip_quality
from app.core.predictor import WeatherPredictor
import pytest

def test_get_risk_assessment():
    assert get_risk_assessment(0.8)["level"] == "BAJO"
    assert get_risk_assessment(0.5)["level"] == "MEDIO"
    assert get_risk_assessment(0.2)["level"] == "ALTO"

def test_generate_smart_feedback():
    # Case 1: Ideal
    feedback = generate_smart_feedback(25, 20, 30)
    assert feedback["title"] == "Clima en Rango"
    
    # Case 2: Too Cold
    feedback = generate_smart_feedback(10, 20, 30)
    assert feedback["title"] == "Demasiado Frío"
    
    # Case 3: Too Hot
    feedback = generate_smart_feedback(36, 20, 30)
    assert feedback["title"] == "Calor Extremo"

def test_analyze_trip_quality():
    forecasts = [
        {"probability": 0.9},
        {"probability": 0.8},
        {"probability": 0.7},
        {"probability": 0.2},
        {"probability": 0.1}
    ]
    summary = analyze_trip_quality(forecasts)
    assert summary["total_days"] == 5
    assert summary["good_days_count"] == 3
    # 3/5 = 60% -> Acceptable (>= 50)
    assert summary["verdict"] == "Viaje Aceptable"

def test_predictor_training(sample_data):
    predictor = WeatherPredictor()
    result = predictor.train(sample_data)
    assert predictor.is_trained
    assert result["n_samples"] > 0
    assert "monthly_sigmas" in result

def test_predictor_prediction(sample_data):
    predictor = WeatherPredictor()
    predictor.train(sample_data)
    
    # Predict for a date in the future
    result = predictor.predict_probability("04-02-2026", 27, "equal", 2.5)
    assert "probability" in result
    assert 0 <= result["probability"] <= 1

from pydantic import BaseModel, Field
from typing import Dict, Any, List, Optional

class PredictionRequest(BaseModel):
    data: Dict[str, Any] = Field(..., description="The full NASA/POWER JSON dataset")
    condition: float = Field(..., description="Temperature threshold (e.g., 20)")
    criterio: str = Field(..., description="Criterion: 'more', 'less', or 'equal'")
    date: str = Field(..., description="Target date in DD-MM-YYYY format")
    tolerance: float = Field(1.0, description="Window size for 'equal' (e.g. 3.0 means target +/- 3 deg)")

class TripPredictionRequest(BaseModel):
    data: Dict[str, Any] = Field(..., description="NASA JSON Data")
    start_date: str = Field(..., description="Inicio del viaje (DD-MM-YYYY)")
    end_date: str = Field(..., description="Fin del viaje (DD-MM-YYYY)")
    min_temp: float = Field(..., description="Mínima tolerable")
    max_temp: float = Field(..., description="Máxima tolerable")

class RangePredictionRequest(BaseModel):
    data: Dict[str, Any] = Field(..., description="NASA JSON Data")
    date: str = Field(..., description="Fecha del viaje (DD-MM-YYYY)")
    min_temp: float = Field(..., description="Mínima temperatura que el usuario tolera")
    max_temp: float = Field(..., description="Máxima temperatura que el usuario tolera")

class RiskAssessment(BaseModel):
    level: str
    color: str
    message: str

class SmartFeedback(BaseModel):
    title: str
    body: str
    icon: str

class TripSummary(BaseModel):
    verdict: str
    message: str
    overall_color: str
    good_days_count: int
    total_days: int

class WeatherResponse(BaseModel):
    probability: float
    probability_percent: str
    predicted_mean: float
    month_volatility_std: float
    window_range: str
    message: str

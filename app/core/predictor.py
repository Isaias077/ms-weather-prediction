import pandas as pd
import numpy as np
from prophet import Prophet
from scipy.stats import norm
from datetime import datetime
import logging

logging.getLogger('cmdstanpy').setLevel(logging.WARNING)
logging.getLogger('prophet').setLevel(logging.WARNING)

class WeatherPredictor:
    def __init__(self):
        self.model = None
        self.is_trained = False
        self.start_date = None
        
        self.monthly_noise_std = {} 
        self.global_noise_std = 0.0

    def preprocess_data(self, data: dict):
        try:
            if "T2M_MAX" in data["properties"]["parameter"]:
                raw_data = data["properties"]["parameter"]["T2M_MAX"]
            else:
                raw_data = data["properties"]["parameter"]["T2M"]

            df = pd.DataFrame(list(raw_data.items()), columns=["date_str", "y"])
            
            fill_value = data.get("header", {}).get("fill_value", -999.0)
            df = df[df["y"] != fill_value]
            
            df["ds"] = pd.to_datetime(df["date_str"], format="%Y%m%d")
            df = df.sort_values("ds")
            
            self.start_date = df["ds"].min()
            return df[["ds", "y"]]
        except Exception as e:
            raise ValueError(f"Error processing data: {e}")

    def train(self, data: dict):
        df = self.preprocess_data(data)
        
        self.model = Prophet(daily_seasonality=False, yearly_seasonality=True, weekly_seasonality=False)
        self.model.fit(df)
        self.is_trained = True
        
        forecast = self.model.predict(df)
        
        df_residuals = df.copy()
        df_residuals['yhat'] = forecast['yhat'].values
        df_residuals['residual'] = df_residuals['y'] - df_residuals['yhat']
        
        df_residuals['month'] = df_residuals['ds'].dt.month
        
        # Calculamos la desviación estándar PARA CADA MES independiente
        self.monthly_noise_std = df_residuals.groupby('month')['residual'].std().to_dict()
        
        self.global_noise_std = df_residuals['residual'].std()
        
        return {
            "n_samples": len(df),
            "monthly_sigmas": self.monthly_noise_std,
            "global_sigma": self.global_noise_std
        }

    def predict_period_probability(self, start_date_str: str, end_date_str: str, condition_temp: float, criterion: str, tolerance: float = 2.5):
        if not self.is_trained:
            raise RuntimeError("Model is not trained.")
            
        start_dt = datetime.strptime(start_date_str, "%d-%m-%Y")
        end_dt = datetime.strptime(end_date_str, "%d-%m-%Y")
        
        date_range = pd.date_range(start=start_dt, end=end_dt)
        future = pd.DataFrame({"ds": date_range})
        
        forecast = self.model.predict(future)
        
        daily_results = []
        
        for index, row in forecast.iterrows():
            date_val = row['ds']
            mean = row['yhat']
            month = date_val.month
            
            # Usamos el Sigma (ruido) específico de ese mes
            current_std = self.monthly_noise_std.get(month, self.global_noise_std)
            
            if criterion == "equal":
                lower = condition_temp - tolerance
                upper = condition_temp + tolerance
                prob = norm.cdf(upper, loc=mean, scale=current_std) - norm.cdf(lower, loc=mean, scale=current_std)
            else:
                prob = 0.0 # Fallback
            
            prob = np.clip(prob, 0.0, 1.0)
            
            daily_results.append({
                "date": date_val.strftime("%d-%m-%Y"),
                "predicted_temp": float(mean),
                "probability": float(prob),
                "probability_percent": float(prob * 100),
                "month_std": float(current_std)
            })
            
        return daily_results

    def predict_probability(self, target_date_str: str, condition_temp: float, criterion: str, tolerance: float = 2.5):
        # NOTA: Puse tolerance por defecto en 2.5 porque si el usuario pide ventana de 5 grados,
        
        if not self.is_trained:
            raise RuntimeError("Model is not trained.")
            
        target_date = datetime.strptime(target_date_str, "%d-%m-%Y")
        target_month = target_date.month
        
        future = pd.DataFrame({"ds": [target_date]})
        forecast = self.model.predict(future)
        mean = forecast["yhat"].values[0]
        
        current_std = self.monthly_noise_std.get(target_month, self.global_noise_std)
        
        if criterion == "more":
            prob = 1 - norm.cdf(condition_temp, loc=mean, scale=current_std)
        elif criterion == "less":
            prob = norm.cdf(condition_temp, loc=mean, scale=current_std)
        elif criterion == "equal":
            lower = condition_temp - tolerance
            upper = condition_temp + tolerance
            prob = norm.cdf(upper, loc=mean, scale=current_std) - norm.cdf(lower, loc=mean, scale=current_std)
        else:
            raise ValueError(f"Invalid criterion: {criterion}")
            
        prob = np.clip(prob, 0.0, 1.0)
            
        return {
            "probability": float(prob),
            "probability_percent": f"{prob*100:.1f}%",
            "predicted_mean": float(mean),
            "month_volatility_std": float(current_std),
            "window_range": f"{condition_temp - tolerance:.1f}°C a {condition_temp + tolerance:.1f}°C",
            "message": f"Probabilidad para ventana de {tolerance*2}°C en este mes."
        }

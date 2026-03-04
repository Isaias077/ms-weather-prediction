# ms-weather-prediction

![Python](https://img.shields.io/badge/Python-3.9%2B-blue?logo=python)
![FastAPI](https://img.shields.io/badge/FastAPI-0.100%2B-009688?logo=fastapi)
![Prophet](https://img.shields.io/badge/Prophet-Facebook-orange)
![License](https://img.shields.io/badge/License-MIT-green)

**ms-weather-prediction** is a microservice that provides a REST API for probabilistic weather predictions. It leverages Facebook's **Prophet** time-series model trained on historical temperature data (e.g., from the [NASA POWER API](https://power.larc.nasa.gov/)) and applies Bayesian inference via Gaussian distributions to compute the likelihood of specific temperature conditions on a given date or date range.

---

## Table of Contents

1. [Overview](#overview)
2. [Technology Stack](#technology-stack)
3. [Project Structure](#project-structure)
4. [Getting Started](#getting-started)
   - [Prerequisites](#prerequisites)
   - [Installation](#installation)
   - [Running the Server](#running-the-server)
5. [Data Source Format](#data-source-format)
6. [API Reference](#api-reference)
   - [Health Check](#health-check)
   - [POST /predict](#1-single-date-prediction)
   - [POST /predict_range](#2-ui-optimized-range-prediction)
   - [POST /predict_trip](#3-trip-viability-prediction)
7. [Running Tests](#running-tests)
8. [Architecture Notes](#architecture-notes)
9. [Contributing](#contributing)

---

## Overview

This microservice solves the following problem: **given years of historical daily temperature records for a location, what is the probability that the temperature on a future date will meet a user-defined condition?**

The prediction pipeline:
1. **Ingests** raw historical temperature data in NASA/POWER JSON format.
2. **Trains** a Prophet model on the fly to capture yearly seasonality and trend.
3. **Computes residuals** to build a per-month noise model (standard deviation per calendar month).
4. **Applies a Gaussian CDF** over the Prophet forecast + per-month noise to calculate the probability that the temperature falls above, below, or within a target range.
5. **Returns** the probability along with user-friendly risk levels and smart feedback.

---

## Technology Stack

| Component       | Technology                                     |
|-----------------|------------------------------------------------|
| Web Framework   | [FastAPI](https://fastapi.tiangolo.com/)       |
| ASGI Server     | [Uvicorn](https://www.uvicorn.org/)            |
| Time-Series ML  | [Prophet (by Meta)](https://facebook.github.io/prophet/) |
| Data Processing | [Pandas](https://pandas.pydata.org/), [NumPy](https://numpy.org/) |
| Statistics      | [SciPy](https://scipy.org/) (`scipy.stats.norm`) |
| Data Validation | [Pydantic](https://docs.pydantic.dev/)         |
| Testing         | [pytest](https://pytest.org/)                  |

---

## Project Structure

```
ms-weather-prediction/
├── app/
│   ├── core/
│   │   ├── predictor.py      # WeatherPredictor: Prophet training + Bayesian inference
│   │   └── utils.py          # Date normalization utilities
│   ├── services.py           # Risk assessment, smart feedback, trip quality analysis
│   ├── schemas.py            # Pydantic request/response models
│   └── main.py               # FastAPI app definition and endpoint routing
├── tests/
│   ├── conftest.py           # Shared pytest fixtures (sample data)
│   ├── test_integration.py   # Integration tests for all API endpoints
│   └── test_unit.py          # Unit tests for services and predictor
├── requirements.txt          # Python dependencies
└── README.md
```

---

## Getting Started

### Prerequisites

- **Python 3.9+**
- **pip** and **virtualenv** (or any virtual environment manager)

### Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/Isaias077/ms-weather-prediction.git
   cd ms-weather-prediction
   ```

2. **Create and activate a virtual environment:**
   ```bash
   # macOS / Linux
   python3 -m venv .venv
   source .venv/bin/activate

   # Windows
   python -m venv .venv
   .venv\Scripts\activate
   ```

3. **Install the dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

### Running the Server

Start the development server from the project root:

```bash
uvicorn app.main:app --reload
```

The API will be available at **`http://127.0.0.1:8000`**.

Interactive API documentation (Swagger UI) is auto-generated at:
- **`http://127.0.0.1:8000/docs`**
- **`http://127.0.0.1:8000/redoc`**

---

## Data Source Format

All prediction endpoints accept historical temperature data in the body of the `POST` request. The expected format follows the **NASA POWER API** response structure:

```json
{
  "properties": {
    "parameter": {
      "T2M": {
        "19900101": 22.5,
        "19900102": 23.1,
        "19900103": 21.8,
        "...": "..."
      }
    }
  }
}
```

- **Key:** Date string in `YYYYMMDD` format.
- **Value:** Daily average (or maximum) temperature in **°C**.
- The service also supports the `T2M_MAX` parameter key.
- Values equal to the NASA fill value (`-999`) are automatically filtered out.

> **Tip:** You can obtain historical data for any location worldwide from the [NASA POWER API](https://power.larc.nasa.gov/api/temporal/daily/point).

---

## API Reference

### Health Check

**`GET /`**

Returns a simple status message confirming the service is running.

```json
{
  "message": "Weather Prediction API is running. Use /predict to calculate probabilities."
}
```

---

### 1. Single Date Prediction

**`POST /predict`**

Calculates the probability that the temperature on a specific date meets the given criterion.

#### Query Parameters

| Parameter   | Type    | Required | Default | Description                                          |
|-------------|---------|----------|---------|------------------------------------------------------|
| `condition` | `float` | ✅       | —       | Temperature threshold in °C                          |
| `criterio`  | `string`| ✅       | —       | Comparison type: `"more"`, `"less"`, or `"equal"`    |
| `date`      | `string`| ✅       | —       | Target date (`DD-MM-YYYY` or `YYYY-MM-DD`)           |
| `tolerance` | `float` | ❌       | `2.5`   | Half-window in °C when `criterio` is `"equal"`       |

#### Request Body

```json
{
  "properties": {
    "parameter": {
      "T2M": {
        "20200101": 24.3,
        "20200102": 25.1
      }
    }
  }
}
```

#### Example Request

```bash
curl -X POST "http://127.0.0.1:8000/predict?condition=25&criterio=more&date=15-07-2025&tolerance=2" \
  -H "Content-Type: application/json" \
  -d '{"properties": {"parameter": {"T2M": {"20200101": 24.3, "20200102": 25.1}}}}'
```

#### Example Response

```json
{
  "probability": 0.6213,
  "probability_percent": "62.1%",
  "predicted_mean": 26.4,
  "month_volatility_std": 2.81,
  "window_range": "22.5°C a 27.5°C",
  "message": "Probabilidad para ventana de 5.0°C en este mes."
}
```

#### Response Fields

| Field                  | Type     | Description                                               |
|------------------------|----------|-----------------------------------------------------------|
| `probability`          | `float`  | Probability value between 0 and 1                         |
| `probability_percent`  | `string` | Human-readable probability (e.g., `"62.1%"`)              |
| `predicted_mean`       | `float`  | Prophet's forecasted mean temperature for the date        |
| `month_volatility_std` | `float`  | Historical noise standard deviation for the target month  |
| `window_range`         | `string` | Temperature window evaluated                              |
| `message`              | `string` | Contextual summary message                                |

---

### 2. UI-Optimized Range Prediction

**`POST /predict_range`**

Designed for slider-based UIs. Accepts a minimum/maximum temperature range for a specific date and returns probability along with a traffic-light risk level and smart user feedback.

#### Query Parameters

| Parameter  | Type    | Required | Description                              |
|------------|---------|----------|------------------------------------------|
| `date`     | `string`| ✅       | Target date (`DD-MM-YYYY` or `YYYY-MM-DD`) |
| `min_temp` | `float` | ✅       | Minimum tolerable temperature in °C      |
| `max_temp` | `float` | ✅       | Maximum tolerable temperature in °C      |

#### Request Body

Same NASA/POWER JSON format as `/predict`.

#### Example Request

```bash
curl -X POST "http://127.0.0.1:8000/predict_range?date=20-08-2025&min_temp=22&max_temp=28" \
  -H "Content-Type: application/json" \
  -d '{"properties": {"parameter": {"T2M": {"20200101": 24.3, "20200102": 25.1}}}}'
```

#### Example Response

```json
{
  "ui_data": {
    "date": "20-08-2025",
    "user_range": "22.0°C - 28.0°C",
    "traffic_light": {
      "level": "BAJO",
      "color": "green",
      "message": "¡Condiciones Ideales!"
    },
    "display_probability": "74.2%",
    "smart_feedback": {
      "title": "Clima en Rango",
      "body": "La temperatura cae justo en tu zona de confort. ¡Dale para adelante!",
      "icon": "😎"
    }
  },
  "scientific_data": {
    "probability": 0.742,
    "probability_percent": "74.2%",
    "predicted_mean": 25.1,
    "month_volatility_std": 2.4,
    "window_range": "22.0°C a 28.0°C",
    "message": "Probabilidad para ventana de 6.0°C en este mes."
  }
}
```

#### Traffic Light Levels

| Color    | Level  | Condition                        |
|----------|--------|----------------------------------|
| 🟢 green  | BAJO   | Probability ≥ 70% — Ideal        |
| 🟡 yellow | MEDIO  | Probability 40–69% — Risky       |
| 🔴 red    | ALTO   | Probability < 40% — Not advised  |

---

### 3. Trip Viability Prediction

**`POST /predict_trip`**

Analyzes a date range to assess the viability of a trip based on daily temperature probabilities.

#### Query Parameters

| Parameter    | Type    | Required | Description                              |
|--------------|---------|----------|------------------------------------------|
| `start_date` | `string`| ✅       | Trip start date (`DD-MM-YYYY`)            |
| `end_date`   | `string`| ✅       | Trip end date (`DD-MM-YYYY`)              |
| `min_temp`   | `float` | ✅       | Minimum tolerable temperature in °C      |
| `max_temp`   | `float` | ✅       | Maximum tolerable temperature in °C      |

#### Request Body

Same NASA/POWER JSON format as `/predict`.

#### Example Request

```bash
curl -X POST "http://127.0.0.1:8000/predict_trip?start_date=01-09-2025&end_date=05-09-2025&min_temp=20&max_temp=30" \
  -H "Content-Type: application/json" \
  -d '{"properties": {"parameter": {"T2M": {"20200101": 24.3, "20200102": 25.1}}}}'
```

#### Example Response

```json
{
  "trip_summary": {
    "verdict": "¡Viaje Excelente!",
    "message": "4 de 5 días tienen condiciones ideales.",
    "overall_color": "green",
    "good_days_count": 4,
    "total_days": 5
  },
  "daily_forecast": [
    {
      "date": "01-09-2025",
      "predicted_temp": 24.8,
      "probability": 0.81,
      "probability_percent": 81.0,
      "month_std": 2.3,
      "status": "IDEAL",
      "icon": "✅"
    }
  ],
  "user_parameters": {
    "range": "20.0°C - 30.0°C",
    "dates": "01-09-2025 al 05-09-2025"
  }
}
```

#### Trip Verdict Levels

| Color    | Verdict              | Condition                         |
|----------|----------------------|-----------------------------------|
| 🟢 green  | ¡Viaje Excelente!    | ≥ 80% of days are ideal           |
| 🟡 yellow | Viaje Aceptable      | 50–79% of days are ideal          |
| 🔴 red    | No recomendado       | < 50% of days are ideal           |

#### Day Status Icons

| Icon | Status   | Probability      |
|------|----------|------------------|
| ✅   | IDEAL    | > 60%            |
| ⚠️   | RIESGOSO | 30–60%           |
| ❌   | MALO     | < 30%            |

---

## Running Tests

This project uses **pytest** for testing. Run the full test suite from the project root:

```bash
pytest
```

For verbose output:

```bash
pytest -v
```

Test coverage includes:
- **Unit tests** (`tests/test_unit.py`): Risk assessment, smart feedback, trip quality analysis, and predictor training/prediction.
- **Integration tests** (`tests/test_integration.py`): Full API endpoint tests using `TestClient`.

---

## Architecture Notes

- **Async execution:** All Prophet training and prediction calls are executed in a separate thread via `asyncio.to_thread()` to avoid blocking the async event loop.
- **Per-month noise modeling:** After training, the predictor calculates the residuals between Prophet's fit and the actual historical data, then computes a standard deviation per calendar month. This per-month sigma is used in the Gaussian CDF to reflect that some months are more volatile than others.
- **Date normalization:** The `normalize_date` utility handles multiple input formats (`DD-MM-YYYY`, `YYYY-MM-DD`, ISO 8601 with time) transparently.

---

## Contributing

1. Fork the repository.
2. Create a feature branch: `git checkout -b feature/my-feature`.
3. Commit your changes: `git commit -m "feat: add my feature"`.
4. Push to the branch: `git push origin feature/my-feature`.
5. Open a Pull Request describing your changes.

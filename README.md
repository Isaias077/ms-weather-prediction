# Bayesian Weather Prediction API

This project provides a FastAPI-based backend to perform Bayesian weather predictions using Facebook's Prophet model. It exposes several endpoints to calculate the probability of certain temperature conditions on specific dates or over a period, based on historical data.

## Project Structure
```
├── app/
│   ├── core/
│   │   └── predictor.py      # Core Prophet model logic
│   ├── services.py           # Business logic (risk, feedback)
│   ├── schemas.py            # Pydantic request/response models
│   └── main.py               # FastAPI application and endpoints
├── tests/
│   ├── test_integration.py   # Integration tests
│   └── test_unit.py          # Unit tests
├── requirements.txt          # Project dependencies
└── README.md                 # This file
```

## Getting Started

### Prerequisites
- Python 3.9+
- Pip and Virtualenv

### Installation

1.  **Clone the repository:**
    ```bash
    git clone <your-repo-url>
    cd weather_backend
    ```

2.  **Create and activate a virtual environment:**
    ```bash
    # For Windows
    python -m venv .venv
    .venv\Scripts\activate

    # For macOS/Linux
    python3 -m venv .venv
    source .venv/bin/activate
    ```

3.  **Install the dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

### Running the Server

To run the application, use `uvicorn` from the project's root directory:

```bash
uvicorn app.main:app --reload
```

The API will be available at `http://127.0.0.1:8000`.

## API Endpoints

The API expects historical weather data formatted as a JSON object, which is passed in the body of each `POST` request.

### 1. Single Date Prediction

Calculates the probability of a temperature condition on a specific date.

- **Endpoint:** `POST /predict`
- **Request Body:**

  ```json
  {
    "data": { "properties": { "parameter": { "T2M": { ... } } } },
    "condition": 25.0,
    "criterio": "more",
    "date": "15-07-2024",
    "tolerance": 2.0
  }
  ```
- **Description:**
  - `data`: The full JSON dataset from the data source (e.g., NASA/POWER).
  - `condition`: The target temperature threshold.
  - `criterio`: The comparison type (`'more'`, `'less'`, or `'equal'`).
  - `date`: The target date in `DD-MM-YYYY` format.
  - `tolerance`: The window used when `criterio` is `'equal'` (e.g., `2.0` means `condition +/- 2.0`).

### 2. UI-Optimized Range Prediction

Optimized for user interfaces like sliders, this calculates the probability that the temperature falls within a given range on a specific date and provides user-friendly feedback.

- **Endpoint:** `POST /predict_range`
- **Request Body:**

  ```json
  {
    "data": { "properties": { "parameter": { "T2M": { ... } } } },
    "date": "20-08-2024",
    "min_temp": 22.0,
    "max_temp": 28.0
  }
  ```

- **Response:** Returns a `ui_data` object with a "traffic light" risk assessment (`green`, `yellow`, `red`) and smart feedback, along with the raw scientific data.

### 3. Trip Viability Prediction

Analyzes a date range to determine the viability of a trip based on a desired temperature range.

- **Endpoint:** `POST /predict_trip`
- **Request Body:**

  ```json
  {
    "data": { "properties": { "parameter": { "T2M": { ... } } } },
    "start_date": "01-09-2024",
    "end_date": "10-09-2024",
    "min_temp": 20.0,
    "max_temp": 30.0
  }
  ```
- **Response:** Returns a trip summary with an overall verdict and color, a count of "good days," and a day-by-day probability breakdown.

## Running Tests

This project uses `pytest` for testing. To run the test suite, execute the following command in the root directory:

```bash
pytest
```

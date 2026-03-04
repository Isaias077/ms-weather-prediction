def test_predict_endpoint(client, sample_data):
    response = client.post(
        "/predict",
        json=sample_data,
        params={
            "condition": 27,
            "criterio": "equal",
            "date": "04-02-2026",
            "tolerance": 2.5,
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert "probability" in data

def test_predict_trip_endpoint(client, sample_data):
    response = client.post(
        "/predict_trip",
        json=sample_data,
        params={
            "start_date": "01-02-2026",
            "end_date": "05-02-2026",
            "min_temp": 20,
            "max_temp": 30,
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert "trip_summary" in data
    assert "daily_forecast" in data

def test_predict_range_endpoint(client, sample_data):
    response = client.post(
        "/predict_range",
        json=sample_data,
        params={
            "date": "04-02-2026",
            "min_temp": 20,
            "max_temp": 30,
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert "ui_data" in data
    assert "scientific_data" in data

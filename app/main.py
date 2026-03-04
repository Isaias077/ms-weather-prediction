from fastapi import FastAPI

from app.api.routes.prediction import router as prediction_router

app = FastAPI(title="Bayesian Weather Prediction API")


@app.get("/")
async def read_root():
    return {"message": "Weather Prediction API is running. Use /predict to calculate probabilities."}


app.include_router(prediction_router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

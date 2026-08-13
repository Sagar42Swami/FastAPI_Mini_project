from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from pydantic import BaseModel, Field
from typing import List
import joblib


app = FastAPI(
    title="BrewPredict API",
    description="FastAPI application for managing teas and making ML predictions",
    version="1.0.0"
)


# -----------------------------
# Load ML Model
# -----------------------------

try:
    model = joblib.load("model.pkl")
except FileNotFoundError:
    model = None


# -----------------------------
# Tea Model
# -----------------------------

class Tea(BaseModel):
    name: str = Field(..., min_length=1)
    flavor: str = Field(..., min_length=1)
    price: float = Field(..., gt=0)


# Request model for prediction
class PredictionRequest(BaseModel):
    data: List[float] = Field(..., min_length=1)


# Response model
class PredictionResponse(BaseModel):
    prediction: int


# -----------------------------
# In-memory database
# -----------------------------

teas: List[Tea] = []


# -----------------------------
# Root Endpoint
# -----------------------------

@app.get("/", response_class=HTMLResponse)
def read_root():
    try:
        with open("index.html", "r", encoding="utf-8") as f:
            return HTMLResponse(content=f.read(), status_code=200)
    except FileNotFoundError:
        return HTMLResponse(content="<h1>BrewPredict Dashboard: index.html not found</h1>", status_code=404)


# -----------------------------
# GET all teas
# -----------------------------

@app.get("/teas", response_model=List[Tea])
def get_teas():
    return teas


# -----------------------------
# GET single tea
# -----------------------------

@app.get("/teas/{tea_id}", response_model=Tea)
def get_tea(tea_id: int):

    if tea_id < 0 or tea_id >= len(teas):
        raise HTTPException(
            status_code=404,
            detail="Tea not found"
        )

    return teas[tea_id]


# -----------------------------
# CREATE tea
# -----------------------------

@app.post("/teas", response_model=Tea, status_code=201)
def create_tea(tea: Tea):
    teas.append(tea)
    return tea


# -----------------------------
# UPDATE tea
# -----------------------------

@app.put("/teas/{tea_id}", response_model=Tea)
def update_tea(tea_id: int, updated_tea: Tea):

    if tea_id < 0 or tea_id >= len(teas):
        raise HTTPException(
            status_code=404,
            detail="Tea not found"
        )

    teas[tea_id] = updated_tea

    return updated_tea


# -----------------------------
# DELETE tea
# -----------------------------

@app.delete("/teas/{tea_id}", response_model=Tea)
def delete_tea(tea_id: int):

    if tea_id < 0 or tea_id >= len(teas):
        raise HTTPException(
            status_code=404,
            detail="Tea not found"
        )

    return teas.pop(tea_id)


# -----------------------------
# ML Prediction
# -----------------------------

@app.post("/predict", response_model=PredictionResponse)
def predict(request: PredictionRequest):

    if model is None:
        raise HTTPException(
            status_code=500,
            detail="ML model is not loaded. Make sure model.pkl exists."
        )

    try:
        result = model.predict([request.data])

        return {
            "prediction": int(result[0])
        }

    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=f"Prediction failed: {str(e)}"
        )
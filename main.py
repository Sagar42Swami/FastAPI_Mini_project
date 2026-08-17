from fastapi import FastAPI, HTTPException, Depends
from fastapi.responses import HTMLResponse
from pydantic import BaseModel, Field
from typing import List, Dict, Any
import joblib
import os
from sqlalchemy.orm import Session
from sqlalchemy import func

import models
from database import SessionLocal, engine

# Create the database tables
models.Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="BrewPredict API",
    description="FastAPI application for managing teas, tracking brews, and making ML predictions",
    version="1.1.0"
)

# -----------------------------
# Dependency: Get DB Session
# -----------------------------
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# -----------------------------
# Load ML Model
# -----------------------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

try:
    model = joblib.load(os.path.join(BASE_DIR, "model.pkl"))
except FileNotFoundError:
    model = None

# -----------------------------
# Pydantic Schemas
# -----------------------------
class TeaBase(BaseModel):
    name: str = Field(..., min_length=1)
    flavor: str = Field(..., min_length=1)
    price: float = Field(..., gt=0)

class TeaCreate(TeaBase):
    pass

class TeaResponse(TeaBase):
    id: int

    class Config:
        from_attributes = True

class BrewLogCreate(BaseModel):
    tea_id: int
    duration_seconds: int = Field(..., gt=0)
    rating: int = Field(..., ge=1, le=5)

class BrewLogResponse(BaseModel):
    id: int
    tea_id: int
    duration_seconds: int
    rating: int
    brewed_at: str

    class Config:
        from_attributes = True

# Request model for prediction
class PredictionRequest(BaseModel):
    data: List[float] = Field(..., min_length=4, max_length=4)

# Response model
class PredictionResponse(BaseModel):
    prediction: int

# -----------------------------
# Root Endpoint
# -----------------------------
@app.get("/", response_class=HTMLResponse)
def read_root():
    try:
        index_path = os.path.join(BASE_DIR, "index.html")
        with open(index_path, "r", encoding="utf-8") as f:
            return HTMLResponse(content=f.read(), status_code=200)
    except FileNotFoundError:
        return HTMLResponse(content="<h1>BrewPredict Dashboard: index.html not found</h1>", status_code=404)

# -----------------------------
# GET all teas
# -----------------------------
@app.get("/teas", response_model=List[TeaResponse])
def get_teas(db: Session = Depends(get_db)):
    return db.query(models.Tea).all()

# -----------------------------
# GET single tea
# -----------------------------
@app.get("/teas/{tea_id}", response_model=TeaResponse)
def get_tea(tea_id: int, db: Session = Depends(get_db)):
    db_tea = db.query(models.Tea).filter(models.Tea.id == tea_id).first()
    if not db_tea:
        raise HTTPException(status_code=404, detail="Tea not found")
    return db_tea

# -----------------------------
# CREATE tea
# -----------------------------
@app.post("/teas", response_model=TeaResponse, status_code=201)
def create_tea(tea: TeaCreate, db: Session = Depends(get_db)):
    db_tea = models.Tea(name=tea.name, flavor=tea.flavor, price=tea.price)
    db.add(db_tea)
    db.commit()
    db.refresh(db_tea)
    return db_tea

# -----------------------------
# UPDATE tea
# -----------------------------
@app.put("/teas/{tea_id}", response_model=TeaResponse)
def update_tea(tea_id: int, updated_tea: TeaCreate, db: Session = Depends(get_db)):
    db_tea = db.query(models.Tea).filter(models.Tea.id == tea_id).first()
    if not db_tea:
        raise HTTPException(status_code=404, detail="Tea not found")
    
    db_tea.name = updated_tea.name
    db_tea.flavor = updated_tea.flavor
    db_tea.price = updated_tea.price
    db.commit()
    db.refresh(db_tea)
    return db_tea

# -----------------------------
# DELETE tea
# -----------------------------
@app.delete("/teas/{tea_id}", response_model=TeaResponse)
def delete_tea(tea_id: int, db: Session = Depends(get_db)):
    db_tea = db.query(models.Tea).filter(models.Tea.id == tea_id).first()
    if not db_tea:
        raise HTTPException(status_code=404, detail="Tea not found")
    
    db.delete(db_tea)
    db.commit()
    return db_tea

# -----------------------------
# BREW Session Endpoints
# -----------------------------
@app.post("/brews", response_model=BrewLogResponse, status_code=201)
def log_brew(brew: BrewLogCreate, db: Session = Depends(get_db)):
    db_tea = db.query(models.Tea).filter(models.Tea.id == brew.tea_id).first()
    if not db_tea:
        raise HTTPException(status_code=404, detail="Tea not found")
    
    db_brew = models.BrewLog(
        tea_id=brew.tea_id,
        duration_seconds=brew.duration_seconds,
        rating=brew.rating
    )
    db.add(db_brew)
    db.commit()
    db.refresh(db_brew)
    
    # Return formatted datetime
    return BrewLogResponse(
        id=db_brew.id,
        tea_id=db_brew.tea_id,
        duration_seconds=db_brew.duration_seconds,
        rating=db_brew.rating,
        brewed_at=db_brew.brewed_at.strftime("%Y-%m-%d %H:%M:%S")
    )

@app.get("/brews", response_model=List[Dict[str, Any]])
def get_brews(db: Session = Depends(get_db)):
    brews = db.query(models.BrewLog).order_by(models.BrewLog.brewed_at.desc()).all()
    result = []
    for b in brews:
        result.append({
            "id": b.id,
            "tea_id": b.tea_id,
            "tea_name": b.tea.name if b.tea else "Unknown",
            "duration_seconds": b.duration_seconds,
            "rating": b.rating,
            "brewed_at": b.brewed_at.strftime("%Y-%m-%d %H:%M:%S")
        })
    return result

# -----------------------------
# ANALYTICS Endpoint
# -----------------------------
@app.get("/analytics")
def get_analytics(db: Session = Depends(get_db)):
    total_teas = db.query(func.count(models.Tea.id)).scalar() or 0
    total_brews = db.query(func.count(models.BrewLog.id)).scalar() or 0
    avg_price = db.query(func.avg(models.Tea.price)).scalar() or 0.0
    avg_rating = db.query(func.avg(models.BrewLog.rating)).scalar() or 0.0
    
    # Flavor distribution
    flavors = db.query(models.Tea.flavor, func.count(models.Tea.id)).group_by(models.Tea.flavor).all()
    flavor_dist = {f[0]: f[1] for f in flavors}
    
    # Brew rating counts
    ratings = db.query(models.BrewLog.rating, func.count(models.BrewLog.id)).group_by(models.BrewLog.rating).all()
    rating_dist = {r[0]: r[1] for r in ratings}

    return {
        "total_teas": total_teas,
        "total_brews": total_brews,
        "average_price": round(avg_price, 2),
        "average_rating": round(avg_rating, 1),
        "flavor_distribution": flavor_dist,
        "rating_distribution": rating_dist
    }

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
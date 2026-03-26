from fastapi import FastAPI
from pydantic import BaseModel
from typing import List

app = FastAPI()

class Tea(BaseModel):
    name: str
    flavor: str
    price: float
    
    
teas : List[Tea] = []


#decorators
@app.get("/")
def read_root():
    return {"message": "Welcome to the Tea API!"}

@app.get("/teas")
def get_teas():
    return teas

@app.post("/teas")
def create_tea(tea: Tea):
    teas.append(tea)
    return tea

@app.put("/teas/{tea_id}")
def update_tea(tea_id: int, updated_tea: Tea):
    if tea_id < len(teas):
        teas[tea_id] = updated_tea
        return updated_tea
    return {"error": "Tea not found"}

@app.delete("/teas/{tea_id}")
def delete_tea(tea_id: int):
    if tea_id < len(teas):
        return teas.pop(tea_id)
    return {"error": "Tea not found"}

@app.post("/predict")
def predict(data: List[float]):
    result = model.predict([data])
    return {"prediction": int(result[0])}
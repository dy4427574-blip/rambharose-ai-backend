from fastapi import FastAPI, Form
from fastapi.middleware.cors import CORSMiddleware
import random

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

VIP_KEY = "$mahakal"

@app.get("/")
def root():
    return {"status": "Rambharose AI backend running"}

@app.post("/predict")
def predict(key: str = Form(...)):
    if key != VIP_KEY:
        return {"error": "Invalid VIP key"}

    prediction = random.choice(["BIG", "SMALL"])

    return {
        "prediction": prediction
    }

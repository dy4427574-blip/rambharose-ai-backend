from fastapi import FastAPI, UploadFile, File, Form
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
def home():
    return {"status": "Rambharose AI backend running"}

@app.post("/predict")
async def predict(
    file: UploadFile = File(...),
    key: str = Form(...)
):
    if key != VIP_KEY:
        return {"error": "Invalid VIP key"}

    # AI-style Big/Small probability logic
    weight = random.random()

    if weight > 0.55:
        prediction = "BIG"
        confidence = round(60 + weight * 20, 2)
    else:
        prediction = "SMALL"
        confidence = round(60 + (1 - weight) * 20, 2)

    return {
        "prediction": prediction,
        "confidence": f"{confidence}%",
        "risk": "Medium"
    }

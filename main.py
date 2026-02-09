from fastapi import FastAPI, Form, HTTPException
import random
import time

app = FastAPI(title="DY Gamer Prediction", version="1.0")

# ---- BASIC ----
@app.get("/")
def root():
    return {"status": "DY Gamer Prediction API Running"}

@app.get("/health")
def health():
    return {"status": "ok", "time": time.time()}

# ---- PREDICTION ----
@app.post("/predict")
def predict(key: str = Form(...)):
    # temporary free mode (no key validation yet)
    prediction = random.choice(["BIG", "SMALL"])
    return {
        "prediction": prediction,
        "confidence": "medium"
    }

from fastapi import FastAPI, Form, HTTPException
import os
import time
import random
from datetime import datetime

app = FastAPI(
    title="DY Gamer Prediction",
    version="1.0"
)

# ===============================
# CONFIG
# ===============================
ADMIN_SECRET = os.getenv("ADMIN_SECRET")

if not ADMIN_SECRET:
    raise RuntimeError("ADMIN_SECRET not set in environment variables")

# ===============================
# IN-MEMORY STORAGE (TEMP)
# ===============================
KEY_DB = {}  
# format:
# key: {
#   "type": "Premium",
#   "expiry": "2026-02-10",
#   "limit": 10,
#   "used": 0,
#   "active": True
# }

# ===============================
# BASIC ROUTES
# ===============================
@app.get("/")
def root():
    return {"status": "DY Gamer Prediction API Running"}

@app.get("/health")
def health():
    return {"status": "ok", "time": time.time()}

# ===============================
# ADMIN ROUTES
# ===============================
@app.post("/admin/add-key")
def add_key(
    admin_secret: str = Form(...),
    key: str = Form(...),
    type: str = Form(...),
    expiry: str = Form(...),
    limit: int = Form(...)
):
    if admin_secret != ADMIN_SECRET:
        raise HTTPException(status_code=403, detail="Invalid admin secret")

    KEY_DB[key] = {
        "type": type,
        "expiry": expiry,
        "limit": limit,
        "used": 0,
        "active": True
    }

    return {
        "status": "success",
        "message": "Key added",
        "key": key
    }


@app.post("/admin/disable-key")
def disable_key(
    admin_secret: str = Form(...),
    key: str = Form(...)
):
    if admin_secret != ADMIN_SECRET:
        raise HTTPException(status_code=403, detail="Invalid admin secret")

    if key not in KEY_DB:
        raise HTTPException(status_code=404, detail="Key not found")

    KEY_DB[key]["active"] = False

    return {
        "status": "success",
        "message": "Key disabled",
        "key": key
    }

# ===============================
# PREDICTION ROUTE
# ===============================
@app.post("/predict")
def predict(key: str = Form(...)):
    if key not in KEY_DB:
        raise HTTPException(status_code=401, detail="Invalid key")

    data = KEY_DB[key]

    if not data["active"]:
        raise HTTPException(status_code=403, detail="Key disabled")

    if data["used"] >= data["limit"]:
        raise HTTPException(status_code=403, detail="Usage limit reached")

    if datetime.today().date() > datetime.fromisoformat(data["expiry"]).date():
        raise HTTPException(status_code=403, detail="Key expired")

    data["used"] += 1

    prediction = random.choice(["BIG", "SMALL"])

    return {
        "prediction": prediction,
        "confidence": "medium",
        "used": data["used"],
        "remaining": data["limit"] - data["used"]
    }

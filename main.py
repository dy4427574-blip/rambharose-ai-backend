from fastapi import FastAPI, Form, HTTPException
import os
import time

app = FastAPI(title="DY Gamer Prediction", version="1.0")

# =====================
# CONFIG
# =====================
ADMIN_SECRET = os.getenv("ADMIN_SECRET")  # Render env variable

if not ADMIN_SECRET:
    raise RuntimeError("ADMIN_SECRET not set in environment")

# In-memory key store (abhi simple rakhenge)
KEYS = {}  
# format:
# key: { "active": True, "limit": 10, "used": 0 }

# =====================
# BASIC
# =====================
@app.get("/")
def root():
    return {"status": "DY Gamer Prediction API Running"}

@app.get("/health")
def health():
    return {"status": "ok", "time": time.time()}

# =====================
# ADMIN
# =====================
@app.post("/admin/add-key")
def add_key(
    admin_secret: str = Form(...),
    key: str = Form(...),
    limit: int = Form(...)
):
    if admin_secret != ADMIN_SECRET:
        raise HTTPException(status_code=403, detail="Invalid admin secret")

    KEYS[key] = {
        "active": True,
        "limit": limit,
        "used": 0
    }

    return {
        "status": "key added",
        "key": key,
        "limit": limit
    }


@app.post("/admin/disable-key")
def disable_key(
    admin_secret: str = Form(...),
    key: str = Form(...)
):
    if admin_secret != ADMIN_SECRET:
        raise HTTPException(status_code=403, detail="Invalid admin secret")

    if key not in KEYS:
        raise HTTPException(status_code=404, detail="Key not found")

    KEYS[key]["active"] = False
    return {"status": "key disabled", "key": key}

# =====================
# PREDICTION
# =====================
@app.post("/predict")
def predict(key: str = Form(...)):
    if key not in KEYS:
        raise HTTPException(status_code=403, detail="Invalid key")

    key_data = KEYS[key]

    if not key_data["active"]:
        raise HTTPException(status_code=403, detail="Key disabled")

    if key_data["used"] >= key_data["limit"]:
        raise HTTPException(status_code=403, detail="Key limit exceeded")

    key_data["used"] += 1

    # ---- LOGIC (temporary manual bias, not random) ----
    prediction = "BIG"  # abhi manual logic
    confidence = "medium"

    return {
        "prediction": prediction,
        "confidence": confidence,
        "used": key_data["used"],
        "limit": key_data["limit"]
    }

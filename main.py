from fastapi import FastAPI, Form, HTTPException
import time
import random

app = FastAPI(title="DY Gamer Prediction", version="1.0")

# ---------------- CONFIG ----------------
ADMIN_SECRET = "deshraj@9302418380"  # sirf server me rahega

# key storage (temporary – memory)
KEYS = {}
# example:
# KEYS["dy123"] = {
#   "type": "Premium",
#   "expiry": "2026-02-10",
#   "limit": 10,
#   "used": 0,
#   "active": True
# }

# ---------------- BASIC ----------------
@app.get("/")
def root():
    return {"status": "DY Gamer Prediction API Running"}

@app.get("/health")
def health():
    return {"status": "ok", "time": time.time()}

# ---------------- ADMIN ----------------
@app.post("/admin/add-key")
def add_key(
    admin_secret: str = Form(...),
    key: str = Form(...),
    type: str = Form(...),
    expiry: str = Form(...),
    limit: int = Form(...)
):
    if admin_secret != ADMIN_SECRET:
        raise HTTPException(status_code=401, detail="Invalid admin secret")

    KEYS[key] = {
        "type": type,
        "expiry": expiry,
        "limit": limit,
        "used": 0,
        "active": True
    }

    return {
        "status": "key created",
        "key": key,
        "details": KEYS[key]
    }


@app.post("/admin/disable-key")
def disable_key(
    admin_secret: str = Form(...),
    key: str = Form(...)
):
    if admin_secret != ADMIN_SECRET:
        raise HTTPException(status_code=401, detail="Invalid admin secret")

    if key not in KEYS:
        raise HTTPException(status_code=404, detail="Key not found")

    KEYS[key]["active"] = False

    return {
        "status": "key disabled",
        "key": key
    }

# ---------------- PREDICTION ----------------
@app.post("/predict")
def predict(key: str = Form(...)):
    if key not in KEYS:
        raise HTTPException(status_code=403, detail="Invalid key")

    data = KEYS[key]

    if not data["active"]:
        raise HTTPException(status_code=403, detail="Key disabled")

    if data["used"] >= data["limit"]:
        raise HTTPException(status_code=403, detail="Key limit reached")

    # use count increase
    data["used"] += 1

    prediction = random.choice(["BIG", "SMALL"])

    return {
        "prediction": prediction,
        "confidence": "medium",
        "used": data["used"],
        "remaining": data["limit"] - data["used"]
    }

from fastapi import FastAPI, UploadFile, File, Form, HTTPException
import os
from datetime import date

app = FastAPI(title="Rambharose AI Backend")

# ======================
# ENV VARIABLES
# ======================
ADMIN_SECRET = os.getenv("ADMIN_SECRET", "")
if not ADMIN_SECRET:
    raise RuntimeError("ADMIN_SECRET not set")

# In-memory key store (simple version)
KEY_DB = {}

# ======================
# ROOT
# ======================
@app.get("/")
def root():
    return {"status": "Rambharose AI running"}

# ======================
# ADMIN: ADD KEY
# ======================
@app.post("/admin/add-key")
def add_key(
    admin_secret: str = Form(...),
    key: str = Form(...),
    key_type: str = Form(...),
    expiry: str = Form(...),
    limit: int = Form(...)
):
    if admin_secret != ADMIN_SECRET:
        raise HTTPException(status_code=401, detail="Invalid admin secret")

    KEY_DB[key] = {
        "type": key_type,
        "expiry": expiry,
        "limit": limit,
        "used": 0,
        "active": True
    }

    return {"status": "Key created", "key": key}

# ======================
# ADMIN: DISABLE KEY
# ======================
@app.post("/admin/disable-key")
def disable_key(
    admin_secret: str = Form(...),
    key: str = Form(...)
):
    if admin_secret != ADMIN_SECRET:
        raise HTTPException(status_code=401, detail="Invalid admin secret")

    if key not in KEY_DB:
        raise HTTPException(status_code=404, detail="Key not found")

    KEY_DB[key]["active"] = False
    return {"status": "Key disabled", "key": key}

# ======================
# PREDICT (BIG / SMALL)
# ======================
@app.post("/predict")
async def predict(
    key: str = Form(...),
    file: UploadFile = File(...)
):
    if key not in KEY_DB:
        raise HTTPException(status_code=401, detail="Invalid key")

    data = KEY_DB[key]

    if not data["active"]:
        raise HTTPException(status_code=403, detail="Key disabled")

    if data["used"] >= data["limit"]:
        raise HTTPException(status_code=403, detail="Limit exceeded")

    # expiry check (basic)
    if date.fromisoformat(data["expiry"]) < date.today():
        raise HTTPException(status_code=403, detail="Key expired")

    data["used"] += 1

    # 🔮 AI LOGIC (placeholder, later improve)
    prediction = "BIG" if data["used"] % 2 == 0 else "SMALL"

    return {
        "prediction": {
            "big_small": prediction
        }
    }

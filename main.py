from fastapi import FastAPI, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import json, os, random, datetime

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

ADMIN_SECRET = "deshraj@9302418380"
KEYS_FILE = "keys.json"

def load_keys():
    if not os.path.exists(KEYS_FILE):
        return {}
    with open(KEYS_FILE, "r") as f:
        return json.load(f)

def save_keys(data):
    with open(KEYS_FILE, "w") as f:
        json.dump(data, f, indent=2)

@app.get("/")
def root():
    return {"status": "Rambharose AI backend running"}

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
        raise HTTPException(status_code=403, detail="Invalid admin secret")

    keys = load_keys()
    keys[key] = {
        "type": type,
        "expiry": expiry,
        "limit": limit,
        "used": 0,
        "active": True
    }
    save_keys(keys)
    return {"status": "Key created", "key": key}

@app.post("/admin/disable-key")
def disable_key(
    admin_secret: str = Form(...),
    key: str = Form(...)
):
    if admin_secret != ADMIN_SECRET:
        raise HTTPException(status_code=403, detail="Invalid admin secret")

    keys = load_keys()
    if key not in keys:
        raise HTTPException(status_code=404, detail="Key not found")

    keys[key]["active"] = False
    save_keys(keys)
    return {"status": "Key disabled", "key": key}

# ---------------- PREDICT ----------------

@app.post("/predict")
def predict(key: str = Form(...)):
    keys = load_keys()

    if key not in keys:
        raise HTTPException(status_code=403, detail="Invalid key")

    data = keys[key]

    if not data["active"]:
        raise HTTPException(status_code=403, detail="Key disabled")

    if data["used"] >= data["limit"]:
        raise HTTPException(status_code=403, detail="Limit exceeded")

    if datetime.date.today() > datetime.date.fromisoformat(data["expiry"]):
        raise HTTPException(status_code=403, detail="Key expired")

    data["used"] += 1
    save_keys(keys)

    return {
        "prediction": {
            "big_small": random.choice(["BIG", "SMALL"])
        }
    }

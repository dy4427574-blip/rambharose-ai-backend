from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import random

app = FastAPI()

# CORS (frontend / html ke liye)
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
async def predict(
    file: UploadFile = File(...),
    key: str = Form(...)
):
    # VIP key check
    if key != VIP_KEY:
        raise HTTPException(status_code=401, detail="Invalid VIP key")

    # Fake AI logic (abhi free version)
    big_small = random.choice(["BIG", "SMALL"])
    color = random.choice(["RED", "GREEN", "VIOLET"])
    number = random.randint(0, 9)

    return {
        "prediction": {
            "big_small": big_small,
            "color": color,
            "number": number
        }
    }

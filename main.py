from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from PIL import Image
import numpy as np
import os

app = FastAPI(title="DY Gamer Prediction")

# 🔐 ADMIN KEY (ENVIRONMENT)
ADMIN_KEY = os.getenv("ADMIN_KEY")

if not ADMIN_KEY:
    raise RuntimeError("ADMIN_KEY not set")

@app.get("/health")
def health():
    return {"status": "ok"}

@app.post("/predict-from-image")
async def predict_from_image(
    key: str = Form(...),
    image: UploadFile = File(...)
):
    # 🔒 Key check
    if key != ADMIN_KEY:
        raise HTTPException(status_code=401, detail="Invalid admin key")

    # 📷 Load image
    try:
        img = Image.open(image.file).convert("RGB")
    except:
        raise HTTPException(status_code=400, detail="Invalid image")

    arr = np.array(img)

    # 🧠 ANALYSIS
    brightness = arr.mean()
    red_strength = arr[:, :, 0].mean()
    green_strength = arr[:, :, 1].mean()

    # 📊 SIZE LOGIC
    if brightness < 120:
        size = "BIG"
    else:
        size = "SMALL"

    # 🎨 COLOR LOGIC
    if green_strength > red_strength:
        color = "GREEN"
    else:
        color = "RED"

    # 🔢 NUMBER LOGIC (NOT RANDOM)
    base_number = int((brightness + red_strength + green_strength) % 10)

    # Fine tuning
    if size == "BIG":
        number = max(5, base_number)
    else:
        number = min(4, base_number)

    return {
        "number": number,
        "size": size,
        "color": color
    }

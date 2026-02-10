from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from PIL import Image
import numpy as np
import os

app = FastAPI(title="DY Gamer Image Prediction AI")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

ADMIN_KEY = os.getenv("ADMIN_KEY")

def size_of(n):
    return "BIG" if n >= 5 else "SMALL"

def color_of(n):
    if n in [1,3,7,9]:
        return "GREEN"
    if n in [2,4,6,8]:
        return "RED"
    return "VIOLET"

def image_trend_analysis(img: Image.Image):
    arr = np.array(img.convert("L"))
    mean = arr.mean()

    # brightness based pressure (works surprisingly well on charts)
    if mean > 140:
        target_size = "SMALL"
        number = 3
    else:
        target_size = "BIG"
        number = 7

    return number, target_size, color_of(number)

@app.post("/predict-from-image")
async def predict_from_image(
    key: str = Form(...),
    image: UploadFile = File(...)
):
    if key != ADMIN_KEY:
        raise HTTPException(status_code=401, detail="Invalid admin key")

    img = Image.open(image.file)

    number, size, color = image_trend_analysis(img)

    return {
        "number": number,
        "size": size,
        "color": color
    }

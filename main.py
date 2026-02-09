from fastapi import FastAPI, File, UploadFile, Form
from fastapi.middleware.cors import CORSMiddleware
import pytesseract
import cv2
import numpy as np

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

VIP_KEY = "$mahakal"

@app.post("/predict")
async def predict(
    file: UploadFile = File(...),
    key: str = Form(...)
):
    if key != VIP_KEY:
        return {"error": "Invalid VIP key"}

    contents = await file.read()
    np_img = np.frombuffer(contents, np.uint8)
    img = cv2.imdecode(np_img, cv2.IMREAD_GRAYSCALE)

    text = pytesseract.image_to_string(img)

    numbers = [int(c) for c in text if c.isdigit()]

    if len(numbers) < 10:
        return {"error": "Not enough data"}

    recent = numbers[-20:]
    big = len([n for n in recent if n >= 5])
    small = len([n for n in recent if n <= 4])

    if big >= small + 3:
        result = "SMALL"
    elif small >= big + 3:
        result = "BIG"
    else:
        last10 = recent[-10:]
        b2 = len([n for n in last10 if n >= 5])
        s2 = len([n for n in last10 if n <= 4])
        result = "SMALL" if b2 >= s2 else "BIG"

    return {"prediction": result}

from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from PIL import Image
import pytesseract
import cv2
import numpy as np
import io

app = FastAPI(title="DY Gamer Image Predictor", version="2.0")

@app.get("/")
def root():
    return {"status": "Image Prediction API Running"}

# ---------- HELPERS ----------

def number_to_big_small(n: int):
    return "BIG" if n >= 5 else "SMALL"

def analyze(numbers):
    sizes = [number_to_big_small(n) for n in numbers]

    big = sizes.count("BIG")
    small = sizes.count("SMALL")

    # streak
    streak = 1
    for i in range(len(sizes) - 1, 0, -1):
        if sizes[i] == sizes[i - 1]:
            streak += 1
        else:
            break

    # decision (simple but logical)
    if sizes[-1] == "SMALL" and small > big:
        prediction = "BIG"
    elif sizes[-1] == "BIG" and big > small:
        prediction = "SMALL"
    else:
        prediction = "BIG" if big < small else "SMALL"

    return {
        "prediction": prediction,
        "confidence": f"{60 + abs(big - small)}%",
        "stats": {
            "big": big,
            "small": small,
            "last_streak": f"{sizes[-1]} x{streak}"
        }
    }

# ---------- MAIN IMAGE API ----------

@app.post("/predict-from-image")
async def predict_from_image(
    key: str = Form(...),
    image: UploadFile = File(...)
):
    contents = await image.read()
    img = Image.open(io.BytesIO(contents)).convert("L")

    img_np = np.array(img)
    img_np = cv2.threshold(img_np, 150, 255, cv2.THRESH_BINARY)[1]

    text = pytesseract.image_to_string(img_np)

    numbers = []
    for word in text.split():
        if word.isdigit():
            n = int(word)
            if 0 <= n <= 9:
                numbers.append(n)

    if len(numbers) < 10:
        raise HTTPException(
            status_code=400,
            detail="Screenshot me enough numbers nahi mile"
        )

    return analyze(numbers[-50:])

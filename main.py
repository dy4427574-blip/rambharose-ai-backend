from fastapi import FastAPI, UploadFile, Form, HTTPException
from PIL import Image
import pytesseract
import numpy as np
import cv2
import io
import re

app = FastAPI(
    title="DY Gamer Prediction",
    description="Image based WinGo prediction system",
    version="1.0"
)

# ==========================
# CONFIG
# ==========================
ADMIN_KEY = "dy@admin930241"

# ==========================
# IMAGE LOAD & VALIDATE
# ==========================
def load_image(image: UploadFile):
    data = image.file.read()
    img = Image.open(io.BytesIO(data)).convert("RGB")
    w, h = img.size

    if w < 700 or h < 1000:
        raise HTTPException(status_code=400, detail="Invalid screenshot size")

    return img

# ==========================
# CROP GAME HISTORY AREA
# ==========================
def crop_history(img: Image.Image):
    w, h = img.size
    # Bottom part (WinGo history usually here)
    crop_box = (0, int(h * 0.55), w, h)
    return img.crop(crop_box)

# ==========================
# IMAGE PREPROCESSING
# ==========================
def preprocess(img: Image.Image):
    img_np = np.array(img)
    gray = cv2.cvtColor(img_np, cv2.COLOR_RGB2GRAY)

    thresh = cv2.adaptiveThreshold(
        gray,
        255,
        cv2.ADAPTIVE_THRESH_MEAN_C,
        cv2.THRESH_BINARY,
        11,
        2
    )
    return thresh

# ==========================
# OCR NUMBER EXTRACTION
# ==========================
def extract_numbers(img):
    text = pytesseract.image_to_string(
        img,
        config="--psm 6 digits"
    )

    numbers = re.findall(r'\b[0-9]\b', text)
    numbers = [int(n) for n in numbers]

    return numbers

# ==========================
# BIG / SMALL CONVERSION
# ==========================
def convert_big_small(numbers):
    result = []
    for n in numbers:
        if n <= 4:
            result.append("SMALL")
        else:
            result.append("BIG")
    return result

# ==========================
# PREDICTION LOGIC
# ==========================
def predict_logic(bs_list):
    last = bs_list[:10]  # last 10 rounds

    big = last.count("BIG")
    small = last.count("SMALL")

    # Trend-break logic
    if big > small:
        return "SMALL", "trend-break"
    elif small > big:
        return "BIG", "trend-break"
    else:
        return "BIG", "neutral"

# ==========================
# HEALTH CHECK
# ==========================
@app.get("/health")
def health():
    return {"status": "DY Gamer Prediction API Running"}

# ==========================
# IMAGE BASED PREDICTION API
# ==========================
@app.post("/predict-from-image")
def predict_from_image(
    key: str = Form(...),
    image: UploadFile = Form(...)
):
    if key != ADMIN_KEY:
        raise HTTPException(status_code=401, detail="Invalid admin key")

    # Step 1: Load image
    img = load_image(image)

    # Step 2: Crop history
    cropped = crop_history(img)

    # Step 3: Preprocess
    processed = preprocess(cropped)

    # Step 4: OCR
    numbers = extract_numbers(processed)

    if len(numbers) < 5:
        raise HTTPException(status_code=400, detail="Game history not detected")

    # Step 5: Convert
    bs = convert_big_small(numbers)

    # Step 6: Prediction
    prediction, confidence = predict_logic(bs)

    return {
        "status": "success",
        "numbers_detected": numbers[:15],
        "big_small_history": bs[:15],
        "prediction": prediction,
        "confidence": confidence
    }

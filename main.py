from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from PIL import Image, ImageEnhance
import pytesseract
import cv2
import numpy as np
import os
import re
from collections import Counter

app = FastAPI(title="DY Gamer Prediction - Image AI")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

ADMIN_KEY = os.getenv("ADMIN_KEY")

# ---------------- UTILS ----------------

def preprocess_image(img: Image.Image):
    img = img.convert("L")  # grayscale
    enhancer = ImageEnhance.Contrast(img)
    img = enhancer.enhance(2.5)
    img_np = np.array(img)
    img_np = cv2.GaussianBlur(img_np, (5,5), 0)
    _, img_np = cv2.threshold(img_np, 120, 255, cv2.THRESH_BINARY)
    return img_np

def extract_numbers(img_np):
    text = pytesseract.image_to_string(img_np, config="--psm 6 digits")
    nums = re.findall(r"\b\d\b", text)
    return [int(n) for n in nums]

def size_of(n):
    return "BIG" if n >= 5 else "SMALL"

def color_of(n):
    if n in [1,3,7,9]:
        return "GREEN"
    if n in [2,4,6,8]:
        return "RED"
    return "VIOLET"

def deep_analysis(history):
    history = history[:40]

    sizes = [size_of(n) for n in history]
    big = sizes.count("BIG")
    small = sizes.count("SMALL")

    # pressure logic
    target_size = "BIG" if small > big else "SMALL"

    # streak break
    streak = 1
    for i in range(1, len(sizes)):
        if sizes[i] == sizes[0]:
            streak += 1
        else:
            break
    if streak >= 3:
        target_size = "BIG" if sizes[0]=="SMALL" else "SMALL"

    pool = list(range(5,10)) if target_size=="BIG" else list(range(0,5))
    freq = Counter(history)
    pool.sort(key=lambda x: freq.get(x,0))

    number = pool[0]
    return number, target_size, color_of(number)

# ---------------- API ----------------

@app.post("/predict-from-image")
async def predict_from_image(
    key: str = Form(...),
    image: UploadFile = File(...)
):
    if key != ADMIN_KEY:
        raise HTTPException(status_code=401, detail="Invalid admin key")

    img = Image.open(image.file)
    processed = preprocess_image(img)
    history = extract_numbers(processed)

    if len(history) < 10:
        raise HTTPException(
            status_code=400,
            detail="Image unclear, history not enough"
        )

    number, size, color = deep_analysis(history)

    return {
        "number": number,
        "size": size,
        "color": color
    }

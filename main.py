from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from PIL import Image
import pytesseract
import cv2
import numpy as np
import io
import os
import re

app = FastAPI(title="DY Gamer Prediction", version="FINAL")

# ---------------- CORS ----------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------- CONFIG ----------------
ADMIN_KEY = os.getenv("ADMIN_KEY")
if not ADMIN_KEY:
    print("ADMIN_KEY not set")

# ---------------- RULES ----------------
def size_from_number(n):
    return "BIG" if n >= 5 else "SMALL"

def color_from_number(n):
    if n in [1,3,7,9]:
        return "GREEN"
    if n in [2,4,6,8]:
        return "RED"
    return "VIOLET"

# ---------------- IMAGE PROCESS ----------------
def crop_history(img):
    w, h = img.size
    return img.crop((0, int(h*0.55), w, h))

def preprocess(img):
    img = np.array(img)
    gray = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)
    gray = cv2.resize(gray, None, fx=1.4, fy=1.4)
    th = cv2.adaptiveThreshold(
        gray,255,
        cv2.ADAPTIVE_THRESH_MEAN_C,
        cv2.THRESH_BINARY,11,2
    )
    return th

def extract_numbers(img):
    text = pytesseract.image_to_string(img, config="--psm 6 digits")
    nums = re.findall(r'\b[0-9]\b', text)
    return [int(n) for n in nums]

# ---------------- DEEP BIG/SMALL ENGINE ----------------
def deep_big_small(history):
    history = history[:50]
    sizes = [size_from_number(n) for n in history]

    votes = {"BIG":0,"SMALL":0}

    big = sizes.count("BIG")
    small = sizes.count("SMALL")

    # Balance pressure
    if big > small:
        votes["SMALL"] += 2
    elif small > big:
        votes["BIG"] += 2

    # Streak
    streak = 1
    for i in range(1,len(sizes)):
        if sizes[i] == sizes[0]:
            streak += 1
        else:
            break

    if streak >= 3:
        votes["BIG" if sizes[0]=="SMALL" else "SMALL"] += 2
    else:
        votes[sizes[0]] += 1

    # Gap
    last_big = next((i for i,s in enumerate(sizes) if s=="BIG"),None)
    last_small = next((i for i,s in enumerate(sizes) if s=="SMALL"),None)

    if last_big is not None and last_big > 6:
        votes["BIG"] += 1
    if last_small is not None and last_small > 6:
        votes["SMALL"] += 1

    # Final size
    if votes["BIG"] > votes["SMALL"]:
        final_size = "BIG"
    elif votes["SMALL"] > votes["BIG"]:
        final_size = "SMALL"
    else:
        final_size = "BIG" if sizes[0]=="SMALL" else "SMALL"

    # Number selection (non-random)
    if final_size == "BIG":
        pool = [5,6,7,8,9]
    else:
        pool = [0,1,2,3,4]

    last_num = history[0]
    pool = [n for n in pool if n != last_num]

    number = pool[0]
    color = color_from_number(number)

    return number, final_size, color

# ---------------- API ----------------
@app.post("/predict-from-image")
async def predict_from_image(
    key: str = Form(...),
    image: UploadFile = File(...)
):
    if key != ADMIN_KEY:
        raise HTTPException(status_code=401, detail="Invalid key")

    if not image.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="Invalid image")

    img_bytes = await image.read()
    img = Image.open(io.BytesIO(img_bytes)).convert("RGB")

    if img.size[0] < 600 or img.size[1] < 800:
        raise HTTPException(status_code=400, detail="Image too small")

    cropped = crop_history(img)
    processed = preprocess(cropped)
    numbers = extract_numbers(processed)

    if len(numbers) < 20:
        raise HTTPException(status_code=400, detail="Not enough history detected")

    number, size, color = deep_big_small(numbers)

    return {
        "number": number,
        "size": size,
        "color": color
    }

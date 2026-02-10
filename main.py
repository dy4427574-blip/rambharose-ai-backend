from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from PIL import Image
import numpy as np
import easyocr
import io
import os

app = FastAPI(
    title="DY Gamer Prediction",
    version="EASYOCR-1.0"
)

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

# ---------------- OCR INIT (ONCE) ----------------
reader = easyocr.Reader(['en'], gpu=False)

# ---------------- RULES ----------------
def size_from_number(n):
    return "BIG" if n >= 5 else "SMALL"

def color_from_number(n):
    if n in [1,3,7,9]:
        return "GREEN"
    if n in [2,4,6,8]:
        return "RED"
    return "VIOLET"

# ---------------- DEEP BIG/SMALL ENGINE ----------------
def deep_big_small(history):
    history = history[:50]
    sizes = [size_from_number(n) for n in history]

    votes = {"BIG":0, "SMALL":0}

    big = sizes.count("BIG")
    small = sizes.count("SMALL")

    # balance pressure
    if big > small:
        votes["SMALL"] += 2
    elif small > big:
        votes["BIG"] += 2

    # streak
    streak = 1
    for i in range(1, len(sizes)):
        if sizes[i] == sizes[0]:
            streak += 1
        else:
            break

    if streak >= 3:
        votes["BIG" if sizes[0]=="SMALL" else "SMALL"] += 2
    else:
        votes[sizes[0]] += 1

    # final size
    if votes["BIG"] > votes["SMALL"]:
        final_size = "BIG"
    elif votes["SMALL"] > votes["BIG"]:
        final_size = "SMALL"
    else:
        final_size = "BIG" if sizes[0]=="SMALL" else "SMALL"

    # number selection (non-random)
    if final_size == "BIG":
        pool = [5,6,7,8,9]
    else:
        pool = [0,1,2,3,4]

    last_num = history[0]
    pool = [n for n in pool if n != last_num]

    number = pool[0]
    color = color_from_number(number)

    return number, final_size, color

# ---------------- IMAGE → NUMBERS ----------------
def extract_numbers_easyocr(img: Image.Image):
    img_np = np.array(img)
    results = reader.readtext(img_np, detail=0)

    numbers = []
    for txt in results:
        if txt.isdigit():
            n = int(txt)
            if 0 <= n <= 9:
                numbers.append(n)

    return numbers

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

    data = await image.read()
    img = Image.open(io.BytesIO(data)).convert("RGB")

    if img.size[0] < 500 or img.size[1] < 700:
        raise HTTPException(status_code=400, detail="Image too small")

    numbers = extract_numbers_easyocr(img)

    if len(numbers) < 15:
        raise HTTPException(
            status_code=400,
            detail="Not enough numbers detected from image"
        )

    number, size, color = deep_big_small(numbers)

    return {
        "number": number,
        "size": size,
        "color": color
    }

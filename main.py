from fastapi import FastAPI, File, UploadFile, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from PIL import Image
import os
import io
import time

app = FastAPI(
    title="DY Gamer Prediction",
    version="3.0",
    description="Deep analysis based Big/Small prediction"
)

# -------------------------
# CORS
# -------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# -------------------------
# ENV CONFIG
# -------------------------
ADMIN_KEY = os.getenv("ADMIN_KEY")
if not ADMIN_KEY:
    print("⚠️ ADMIN_KEY not set")

# -------------------------
# BASIC ROUTES
# -------------------------
@app.get("/")
def root():
    return {"status": "DY Gamer Prediction API Running"}

@app.get("/health")
def health():
    return {"status": "ok", "time": int(time.time())}

# -------------------------
# HELPER LOGIC (NON-RANDOM)
# -------------------------
def size_from_number(n: int) -> str:
    return "BIG" if n >= 5 else "SMALL"

def color_from_number(n: int) -> str:
    if n in [1, 3, 7, 9]:
        return "GREEN"
    if n in [2, 4, 6, 8]:
        return "RED"
    return "VIOLET"

def deep_big_small_prediction(history_numbers):
    """
    history_numbers: list[int]
    latest -> oldest
    """

    sizes = [size_from_number(n) for n in history_numbers]

    big = sizes.count("BIG")
    small = sizes.count("SMALL")

    # ----- Deep logic (no random) -----
    # 1. Balance bias
    if big > small:
        final_size = "SMALL"
    elif small > big:
        final_size = "BIG"
    else:
        # 2. Streak bias
        final_size = sizes[0]

    # ----- Number selection (supportive) -----
    if final_size == "BIG":
        candidates = [5, 6, 7, 8, 9]
    else:
        candidates = [0, 1, 2, 3, 4]

    last_number = history_numbers[0]
    candidates = [n for n in candidates if n != last_number]

    # deterministic (no random)
    final_number = candidates[0]
    final_color = color_from_number(final_number)

    return final_number, final_size, final_color

# -------------------------
# IMAGE BASED PREDICTION API
# -------------------------
@app.post("/predict-from-image")
async def predict_from_image(
    key: str = Form(...),
    image: UploadFile = File(...)
):
    # ---- Admin key check ----
    if key != ADMIN_KEY:
        raise HTTPException(status_code=401, detail="Invalid admin key")

    # ---- Image validation ----
    if not image.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="Invalid image")

    try:
        contents = await image.read()
        img = Image.open(io.BytesIO(contents)).convert("RGB")

        width, height = img.size
        if width < 600 or height < 800:
            raise HTTPException(status_code=400, detail="Image too small")

        # -----------------------------------
        # TEMP HISTORY (NON-RANDOM, FIXED LOGIC)
        # Latest -> Oldest
        # (Next step me image se yahi extract karenge)
        # -----------------------------------
        history_numbers = [
            2, 4, 3, 1, 0,
            6, 8, 7, 9, 5,
            4, 2, 1, 3, 6
        ]

        final_number, final_size, final_color = deep_big_small_prediction(
            history_numbers
        )

        # ---- FINAL OUTPUT (ONLY 3 THINGS) ----
        return {
            "number": final_number,
            "size": final_size,
            "color": final_color
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

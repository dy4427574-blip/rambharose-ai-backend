from fastapi import FastAPI, File, UploadFile, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from PIL import Image
import os
import io
import time

app = FastAPI(
    title="DY Gamer Prediction",
    version="2.0",
    description="Image based prediction system"
)

# -------------------------
# CORS (safe default)
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
    print("⚠️ ADMIN_KEY not set in environment")

# -------------------------
# BASIC ROUTES
# -------------------------
@app.get("/")
def root():
    return {"status": "DY Gamer Prediction API Running"}

@app.get("/health")
def health():
    return {
        "status": "ok",
        "time": int(time.time())
    }

# -------------------------
# IMAGE PREDICTION
# -------------------------
@app.post("/predict-from-image")
async def predict_from_image(
    key: str = Form(...),
    image: UploadFile = File(...)
):
    # ---- Key validation ----
    if key != ADMIN_KEY:
        raise HTTPException(status_code=401, detail="Invalid admin key")

    # ---- Image validation ----
    if not image.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="Invalid image file")

    try:
        contents = await image.read()
        img = Image.open(io.BytesIO(contents))

        width, height = img.size
        mode = img.mode

        # 🔮 Placeholder prediction logic (upgrade later)
        prediction = "ANALYSIS_ONLY"

        return {
            "status": "success",
            "analysis": {
                "width": width,
                "height": height,
                "mode": mode
            },
            "prediction": prediction
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

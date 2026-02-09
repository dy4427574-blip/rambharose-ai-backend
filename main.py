from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from PIL import Image
import io
import os

app = FastAPI(title="DY Gamer Prediction", version="2.0")

ADMIN_SECRET = os.getenv("ADMIN_SECRET")

@app.get("/")
def root():
    return {"status": "DY Gamer Prediction API Running"}

@app.post("/predict-from-image")
async def predict_from_image(
    key: str = Form(...),
    image: UploadFile = File(...)
):
    # 🔐 Key check
    if key != ADMIN_SECRET:
        raise HTTPException(status_code=401, detail="Invalid key")

    try:
        # 📸 Read image safely
        image_bytes = await image.read()
        img = Image.open(io.BytesIO(image_bytes))
        img = img.convert("RGB")

        width, height = img.size

        # 🔍 Dummy analysis (safe)
        analysis = {
            "width": width,
            "height": height,
            "mode": img.mode,
        }

        # ⚠️ Prediction placeholder (no random)
        prediction = "ANALYSIS_ONLY"

        return {
            "status": "success",
            "analysis": analysis,
            "prediction": prediction
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Image processing failed: {str(e)}"
        )

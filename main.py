from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import requests
from bs4 import BeautifulSoup
import os

app = FastAPI(title="WinGo Prediction Mirror API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

BASE_URL = "https://wingoaisite.com/wingo-prediction/"

def fetch_prediction(mode: str):
    try:
        response = requests.get(BASE_URL, timeout=10)
        soup = BeautifulSoup(response.text, "html.parser")

        # ⚠️ IMPORTANT:
        # Ye class name inspect karke change karna hoga
        # Browser → Right click → Inspect → prediction div ka class copy karo

        if mode == "30s":
            prediction_div = soup.find("div", {"data-mode": "30s"})
        elif mode == "1min":
            prediction_div = soup.find("div", {"data-mode": "1min"})
        else:
            raise HTTPException(status_code=400, detail="Invalid mode")

        if not prediction_div:
            raise HTTPException(status_code=500, detail="Prediction block not found")

        prediction_text = prediction_div.get_text(strip=True)

        return {
            "mode": mode,
            "prediction": prediction_text
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/predict/30s")
def get_30s_prediction():
    return fetch_prediction("30s")


@app.get("/predict/1min")
def get_1min_prediction():
    return fetch_prediction("1min")

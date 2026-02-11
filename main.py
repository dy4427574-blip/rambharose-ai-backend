from fastapi import FastAPI
import requests
from bs4 import BeautifulSoup

app = FastAPI()

TARGET_URL = "https://wingoaisite.com/wingo-prediction/"

@app.get("/")
def home():
    return {"status": "API Working"}

@app.get("/live-prediction")
def get_prediction():
    try:
        response = requests.get(TARGET_URL, timeout=10)
        soup = BeautifulSoup(response.text, "html.parser")

        text = soup.get_text()

        # Simple extraction logic
        if "Green" in text:
            color = "Green"
        elif "Red" in text:
            color = "Red"
        elif "Violet" in text:
            color = "Violet"
        else:
            color = "Not Found"

        if "Big" in text:
            size = "Big"
        elif "Small" in text:
            size = "Small"
        else:
            size = "Not Found"

        return {
            "color": color,
            "size": size
        }

    except Exception as e:
        return {"error": str(e)}

from fastapi import FastAPI, HTTPException
from playwright.sync_api import sync_playwright
import re

app = FastAPI(title="DY Gamer Live Prediction")

TARGET_URL = "https://wingoaisite.com/wingo-prediction/"

@app.get("/")
def root():
    return {"status": "DY Gamer Live Scraper Running"}

@app.get("/live-prediction")
def live_prediction():
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True, args=["--no-sandbox"])
            page = browser.new_page()
            page.goto(TARGET_URL, timeout=60000)
            page.wait_for_timeout(5000)  # wait JS load
            
            content = page.content()
            browser.close()

        # Extract Color
        color_match = re.search(r'Color.*?(Green|Red|Violet)', content, re.IGNORECASE)
        size_match = re.search(r'(Big|Small)', content, re.IGNORECASE)

        if not color_match or not size_match:
            raise Exception("Prediction not found")

        color = color_match.group(1).capitalize()
        size = size_match.group(1).capitalize()

        return {
            "color": color,
            "size": size
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

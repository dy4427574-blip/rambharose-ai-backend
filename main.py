from fastapi import FastAPI

app = FastAPI(title="Rambharose AI", version="1.0")

@app.get("/")
def root():
    return {
        "status": "ok",
        "message": "Rambharose AI backend running"
    }

@app.get("/health")
def health():
    return {"health": "good"}

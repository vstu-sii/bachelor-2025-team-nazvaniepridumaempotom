from fastapi import FastAPI
import os

app = FastAPI(title="AI Cooking Assistant API")

@app.get("/")
async def root():
    return {"message": "AI Cooking Assistant API is running!"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

@app.get("/metrics")
async def metrics():

    return "http_requests_total 0"

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
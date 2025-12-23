
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn

app = FastAPI(title="Food Analysis Backend", version="1.0.0")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

class HealthResponse(BaseModel):
    status: str
    version: str
    service: str = "backend"

@app.get("/")
async def root():
    return {"message": "Food Analysis Backend API"}

@app.get("/health")
async def health():
    return HealthResponse(status="healthy", version="1.0.0")

@app.get("/api/foods")
async def get_foods():
    return {"foods": ["pizza", "salad", "sushi"]}

@app.post("/api/analyze")
async def analyze_food():
    return {"analysis": "Food analysis would go here", "confidence": 0.95}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
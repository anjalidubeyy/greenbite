from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import pickle
import numpy as np
from pydantic import BaseModel

# Load the trained model
MODEL_PATH = r"C:\greenbite\backend\sustainability_model.pkl"

try:
    with open(MODEL_PATH, "rb") as model_file:
        model = pickle.load(model_file)
except Exception as e:
    print(f"🚨 Error loading model: {e}")
    model = None  # Prevent crashes if model fails to load

app = FastAPI()

# Enable CORS for frontend (React)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Change to "*" for testing but NOT in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Define the input data model
class EmissionsData(BaseModel):
    land_use_change: float
    feed: float
    farm: float
    processing: float
    transport: float
    packaging: float
    retail: float
    total_land_to_retail: float

@app.post("/predict")
async def predict_sustainability(data: EmissionsData):
    if model is None:
        return {"error": "Model not loaded. Check logs for issues."}

    try:
        # Convert input data into NumPy array
        input_features = np.array([[
            data.land_use_change, data.feed, data.farm, data.processing,
            data.transport, data.packaging, data.retail, data.total_land_to_retail
        ]])

        # Make prediction
        sustainability_score = model.predict(input_features)[0]

        return {"sustainability_score": round(float(sustainability_score), 2)}
    
    except Exception as e:
        return {"error": str(e)}

# Run server with: uvicorn main:app --reload

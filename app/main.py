from fastapi import FastAPI, UploadFile, File, Form, HTTPException, Query, Depends
from fastapi.responses import JSONResponse, FileResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import numpy as np
import cv2
import logging
from services import DamageDetector, LoadModelPaths, save_output_image
from OurDataBase import SessionLocal, ImageData
import shutil
import os
from datetime import datetime
from ModelTypes import ModelTypeToStr
from sqlalchemy.orm import Session

# ------------------- App Setup -------------------

app = FastAPI()

# Dependency to get the database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Mount static files (JS/CSS)
app.mount("/static", StaticFiles(directory="static"), name="static")

# CORS (optional if frontend is same origin)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load models
PotholePath, WastePath = LoadModelPaths()
Detector = DamageDetector(pothole_model_path=PotholePath, waste_model_path=WastePath)

# ------------------- Frontend Routes -------------------

@app.get("/", response_class=HTMLResponse)
async def serve_index():
    return FileResponse("index.html")

# ------------------- API Routes -------------------

@app.post("/detect")
async def detect_damage(
    file: UploadFile = File(...),
    latitude: float = Form(None),
    longitude: float = Form(None),
    db: Session = Depends(get_db)  # FastAPI injects the Session
) -> JSONResponse:
    try:
        if not file.content_type.startswith("image/"):
            raise HTTPException(status_code=400, detail="File must be an image")

        contents = await file.read()
        nparr = np.frombuffer(contents, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        if img is None:
            raise HTTPException(status_code=400, detail="Could not decode image")

        # Run detection
        Result = Detector.detect_raw_road_damage(img)

        # Save output image
        save_path = save_output_image(Result["raw_output_img_data"], Result["damage_type"])
        logger.debug(f"Image saved at: {save_path}")
        logger.debug(f"Lattiude {latitude}")
        logger.debug(f"longitude {longitude}")

        # Create a new ImageData instance
        image_data = ImageData(
            image_path=save_path,
            detected_type=ModelTypeToStr(Result["damage_type"]),
            latitude=latitude,
            longitude=longitude,
            datetime=datetime.utcnow()
        )
        # Add to the database
        db.add(image_data)
        db.commit()
        db.refresh(image_data)

        return JSONResponse({
            "message": "Report submitted successfully"
        })
    except Exception as e:
        logger.error(f"Error in detect_damage: {str(e)}", exc_info=True)
        return JSONResponse(content={"error": str(e)}, status_code=500)


# Admin panel page
@app.get("/admin", response_class=HTMLResponse)
def admin_panel():
    return FileResponse("admin.html")

# Mock Dashboard panel page
@app.get("/dashboard", response_class=HTMLResponse)
def dashboard_panel():
    return FileResponse("dashboard.html")

import math
from sqlalchemy import and_

class DamageItem(BaseModel):
    id: int
    image_url: str
    latitude: float
    longitude: float
    datetime: datetime
    damage_type: str
    confidence: float

    class Config:
        from_attributes = True

from typing import Dict
from fastapi.responses import JSONResponse

# Remove the response_model since we're returning JSONResponse
@app.get("/api/nearby-damage-point")
async def nearby_damage(
    lat: float = Query(..., description="Current latitude"),
    lon: float = Query(..., description="Current longitude"),
    radius_km: float = Query(1.0, description="Radius in kilometers"),
    db: Session = Depends(get_db)
) -> JSONResponse:
    try:
        import math
        lat_range = radius_km / 111
        lon_range = radius_km / (111 * abs(math.cos(math.radians(lat))) + 1e-6)

        nearby = db.query(ImageData).filter(
            ImageData.latitude.between(lat - lat_range, lat + lat_range),
            ImageData.longitude.between(lon - lon_range, lon + lon_range)
        ).all()

        result = [
            {
                "id": d.id,
                "damage_type": d.detected_type,
                "latitude": d.latitude,
                "longitude": d.longitude,
                "image": d.image_path,
                "datetime": d.datetime.isoformat()
            }
            for d in nearby
        ]

        return result  # FastAPI converts list/dict to JSON automatically
    except Exception as e:
        logger.error(f"Error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# ------------------- Run App -------------------

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
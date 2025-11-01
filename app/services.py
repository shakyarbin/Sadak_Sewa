# -*- coding: utf-8 -*-
from fastapi import UploadFile, File
from typing import Dict, Any
import cv2
import numpy as np
from ultralytics import YOLO
from ModelTypes import ModelType, ModelTypeToStr
from utils import read_image
from huggingface_hub import login
from huggingface_hub import hf_hub_download
import os
import numpy as np
from numpy import ndarray

HG_FACE_API_KEY = "xxxx"

def LoadModelPaths():    
    # Login for Hugging Face
    login(token="HG_FACE_API_KEY")

    # Downloading Models
    # repo_id = Hugging Face repo name
    # filename = exact file you want
   
    Pothole_Model_Path = hf_hub_download(repo_id="cazzz307/Pothole-Finetuned-YoloV8", filename="Yolov8-fintuned-on-potholes.pt", cache_dir="./models")
    Waste_Model_Path  = hf_hub_download(repo_id="turhancan97/yolov8-segment-trash-detection", filename="yolov8m-seg.pt", cache_dir="./models")
   
    # Pothole_Model_Path= "models/models--cazzz307--Pothole-Finetuned-YoloV8"
    # Waste_Model_Path= "models/models--turhancan97--yolov8-segment-trash-detection"
    return Pothole_Model_Path, Waste_Model_Path  

# Define the storage directory
STORAGE_DIR = "static/storage"

# Create the storage directory if it doesn't exist
os.makedirs(STORAGE_DIR, exist_ok=True)

def save_output_image(output_image: ndarray, damage_type: str) -> str:
    # Generate a unique filename based on the damage type and current count
    count = len(os.listdir(STORAGE_DIR)) + 1  # Increment count based on existing files
    filename = f"{damage_type}_{count}.png"  # Example filename format
    output_path = os.path.join(STORAGE_DIR, filename)
    
    # Save the output image (assuming output_image is a numpy array)
    # You may need to convert it to an image format if it's not already
    from PIL import Image
    img = Image.fromarray(output_image)
    img.save(output_path)
    
    return output_path
class DamageDetector:
    def __init__(self, pothole_model_path: str, waste_model_path: str):
        self.models = self.LoadModels(pothole_model_path, waste_model_path)

    def LoadModels(self, Pothole_Model_Path,Waste_Model_Path ):
        models_to_load = [
            (ModelType.POTHOLE , Pothole_Model_Path),
            (ModelType.WASTE, Waste_Model_Path),
        ]
        loaded_models = {}

        # tqdm progress bar
        for modeltype, path in models_to_load:
            model = YOLO(path)
            loaded_models[modeltype] = model
            print(f"✅ {modeltype} loaded successfully.")

        return loaded_models

    # Cell 3 — Detection function for one model
    def run_detection(self, model, img, conf_threshold=0.25):
        results = model(img)
        count = 0
        for r in results:
            for box in r.boxes:
                conf = float(box.conf[0])
                if conf >= conf_threshold:
                    count += 1
        return count, results

    # Cell 4 — Combined damage decision
    def detect_road_damage(self, img_path):
        img = cv2.imread(img_path)
        return self.detect_raw_road_damage(img)
    # Cell 4 — Combined damage decision
    def detect_raw_road_damage(self,img):
        # Run both models
        pothole_count, pothole_results =  self.run_detection(self.models[ModelType.POTHOLE], img, conf_threshold=0.25)
        waste_count, waste_results     = self.run_detection(self.models[ModelType.WASTE], img, conf_threshold=0.25)

        # Collect confidence scores
        pothole_confidences = [float(box.conf[0]) for r in pothole_results for box in r.boxes]
        waste_confidences   = [float(box.conf[0]) for r in waste_results for box in r.boxes]

        # Compute max (or mean) confidence for each model
        pothole_conf = max(pothole_confidences) if pothole_confidences else 0
        waste_conf   = max(waste_confidences) if waste_confidences else 0

        # Decide which is more prominent
        if pothole_count >= waste_count and pothole_conf >= waste_conf and pothole_count > 0:
            damage_type = ModelType.POTHOLE
            results_to_draw = pothole_results
            color = (0, 255, 0)
            confidence = pothole_conf
        elif waste_count > 0:
            damage_type = ModelType.WASTE
            results_to_draw = waste_results
            color = (0, 0, 255)
            confidence = waste_conf
        else:
            damage_type = ModelType.NONE
            results_to_draw = []
            color = (255, 255, 255)
            confidence = 0

        # Annotate image
        for r in results_to_draw:
            for box in r.boxes:
                x1, y1, x2, y2 = map(int, box.xyxy[0])
                conf = float(box.conf[0])
                cv2.rectangle(img, (x1, y1), (x2, y2), color, 2)
                cv2.putText(img, f"{ModelTypeToStr(damage_type)} {conf:.2f}",
                            (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, color, 2)

        return {
            "raw_output_img_data" : img,
            "damage_type": damage_type,
            "pothole_count": pothole_count,
            "waste_count": waste_count,
            "confidence": confidence,
        }

def create_damage_detector(pothole_model_path: str, waste_model_path: str) -> DamageDetector:
    return DamageDetector(pothole_model_path, waste_model_path)
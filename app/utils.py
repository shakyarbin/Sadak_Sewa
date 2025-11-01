# utils.py

import cv2
import numpy as np

def read_image(image_path: str) -> np.ndarray:
    """Read an image from a file path."""
    img = cv2.imread(image_path)
    if img is None:
        raise ValueError(f"Image not found or unable to read: {image_path}")
    return img

def preprocess_image(image: np.ndarray) -> np.ndarray:
    """Preprocess the image for model input."""
    # Resize or normalize the image as needed for the model
    # This is a placeholder for actual preprocessing steps
    return image

def convert_image_to_bytes(image: np.ndarray) -> bytes:
    """Convert an image to bytes for response."""
    _, buffer = cv2.imencode('.jpg', image)
    return buffer.tobytes()
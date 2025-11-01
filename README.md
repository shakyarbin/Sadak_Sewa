# Road Damage Detector

## Overview
The Road Damage Detector is a FastAPI application designed to analyze images of roads to identify and classify damage, specifically focusing on potholes and waste. This application utilizes pre-trained machine learning models to provide accurate detections and is optimized to run on powerful servers.

## Project Structure
```
road-damage-detector
├── app
│   ├── main.py          # Entry point of the FastAPI application
│   ├── models.py        # Data models for request and response validation
│   ├── services.py      # Core logic for image processing and model interaction
│   ├── utils.py         # Utility functions for image handling
│   └── types.py         # Custom types and enumerations
├── requirements.txt      # List of dependencies
├── Dockerfile            # Instructions to build a Docker image
├── .env                  # Environment variables for configuration
└── README.md             # Project documentation
```

## Installation
To set up the project, follow these steps:

1. Clone the repository:
   ```
   git clone <repository-url>
   cd road-damage-detector
   ```

2. Create a virtual environment (optional but recommended):
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows use `venv\Scripts\activate`
   ```

3. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```

## Usage
To run the FastAPI application, execute the following command:
```
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

You can then access the API at `http://<server-ip>:8000`.

### API Endpoints
- **POST /detect**
  - Description: Upload an image of a road to detect damage.
  - Request Body: An image file.
  - Response: JSON object containing the type of damage detected (pothole, waste, none), counts of each type, and confidence scores.

## Docker
To build and run the application in a Docker container, use the following commands:
```
docker build -t road-damage-detector .
docker run -d -p 8000:8000 road-damage-detector
```

## Environment Variables
The application uses environment variables for configuration. Create a `.env` file in the root directory with the following variables:
```
MODEL_PATH_POTHOLE=<path_to_pothole_model>
MODEL_PATH_WASTE=<path_to_waste_model>
```

## Contributing
Contributions are welcome! Please open an issue or submit a pull request for any enhancements or bug fixes.

## License
This project is licensed under the MIT License. See the LICENSE file for details.
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
import uvicorn
import os
from fastapi.staticfiles import StaticFiles

app = FastAPI()

# Get the current directory
CURRENT_DIR = os.path.dirname(os.path.realpath(__file__))

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files (JS, CSS, images)
app.mount("/static", StaticFiles(directory=CURRENT_DIR), name="static")

@app.get("/")
async def serve_index():
    return FileResponse(os.path.join(CURRENT_DIR, "index.html"))

if __name__ == "__main__":
    print("Starting frontend server on http://localhost:3000")
    uvicorn.run(app, host="0.0.0.0", port=3000)
# app/main.py
from fastapi import FastAPI, WebSocket
from fastapi.middleware.cors import CORSMiddleware
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
)

# Import routers
from app.routers import camera, marker_detection, camera_calibration
from app.routers.camera import websocket_endpoint

app = FastAPI(title="MoCap4All API")

# Configure CORS
origins = [
    "http://localhost:5173",  # React Vite default port
    "http://localhost:3000",
    "*",  # Allow all origins for development - restrict in production
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# WebSocket routes
@app.websocket("/ws/camera/{camera_id}")
async def camera_websocket(websocket: WebSocket, camera_id: str):
    await websocket_endpoint(websocket, camera_id)

# HTTP API routes
app.include_router(camera.router, prefix="/api", tags=["Camera"])
app.include_router(marker_detection.router, prefix="/api", tags=["Marker Detection"])
app.include_router(camera_calibration.router, prefix="/api", tags=["Camera Calibration"])

@app.get("/")
async def root():
    return {"message": "Welcome to MoCap4All API"}

@app.get("/health")
async def health_check():
    return {"status": "ok"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
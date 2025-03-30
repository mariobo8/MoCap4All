# MoCap4All

A motion capture system built with Python FastAPI backend and React frontend using Vite.

## Project Structure

```
MoCap4All/
├── backend/
│   ├── app/
│   │   ├── routers/
│   │   ├── models/
│   │   ├── utils/
│   │   ├── services/
│   │   └── main.py
│   └── requirements.txt
└── frontend/
    ├── public/
    ├── src/
    ├── package.json
    └── vite.config.js
```

## Getting Started

### Backend Setup

1. Navigate to the backend directory:
   ```
   cd backend
   ```

2. Run the FastAPI server:
   ```
   uvicorn app.main:app --reload
   ```

3. Access the API documentation at: `http://localhost:8000/docs`

### Frontend Setup

1. Navigate to the frontend directory:
   ```
   cd frontend
   ```

2. Install dependencies (if not already done):
   ```
   npm install
   ```

3. Start the development server:
   ```
   npm run dev
   ```

4. Access the frontend at: `http://localhost:5173`

## Tech Stack

- **Backend**:
  - FastAPI (Python web framework)
  - OpenCV for image processing
  - MediaPipe for motion tracking
  - SQLAlchemy for database operations

- **Frontend**:
  - React with Vite
  - Three.js for 3D visualization
  - React Three Fiber
  - Material UI for styling
  - Chart.js for data visualization

## Future Components

- Camera calibration
- Motion tracking
- Pose estimation
- 3D visualization
- Data export for robotics
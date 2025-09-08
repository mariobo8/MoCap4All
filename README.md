# MoCap4All 🤖

> A Real-Time 3D Motion Capture System for Robotics

MoCap4All is a cost-effective, multi-camera 3D motion capture system designed for robotics applications. The system uses multiple modified **PlayStation Eye cameras** to track the 3D position of infrared (IR) markers in real-time. The backend is powered by **Python** with **OpenCV** for all computer vision processing, while the frontend is a **React**-based web interface for live visualization and control.

---

## 🏛️ Core Architecture

-   **Backend**: A **Python Flask** server manages all core logic, including camera communication, image processing, and 3D calculations.
-   **Frontend**: A **React** web application serves as the user interface for live visualization and system control.
-   **Communication**: **Flask-SocketIO** (WebSockets) provides the low-latency, real-time communication layer between the backend and frontend.

---

## 🚀 Getting Started

### ✅ Prerequisites

-   Python 3.11
-   Node.js and npm
-   Git

### 📸 Hardware

This system is designed to work with a minimum of 3 **PlayStation Eye cameras**. Each camera must be physically modified by replacing the internal IR-blocking filter with an **IR-pass filter**. This allows the camera to see only infrared light, which is essential for marker detection.

### 💾 Installation

1.  **Clone the repository:**
    ```bash
    git clone git@github.com:mariobo8/MoCap4All.git
    cd MoCap4All
    ```

2.  **Setup the Backend (Python):**
    ```bash
    # Navigate to the backend directory
    cd backend

    # Create a virtual environment
    python -m venv venv

    # Activate the environment
    # On Windows (PowerShell):
    .\venv\Scripts\activate
    # On macOS/Linux:
    # source venv/bin/activate

    # Install dependencies
    pip install -r requirements.txt
    ```

3.  **Setup the Frontend (React):**
    ```bash
    # Navigate to the frontend directory from the root
    cd ../frontend

    # Install dependencies
    npm install
    ```

---

## 🏃 Running the Application

*You will need two separate terminals to run both the backend and frontend servers simultaneously.*

1.  **Start the Backend Server:**
    *(In Terminal 1, from the project root)*
    ```bash
    # Navigate to the backend folder
    cd backend

    # Make sure your virtual environment is active
    python app.py
    ```

2.  **Start the Frontend Application:**
    *(In Terminal 2, from the project root)*
    ```bash
    # Navigate to the frontend folder
    cd frontend

    # This will open the app in your browser
    npm start
    ```

You can now access the web interface by navigating to `http://localhost:3000` in your browser.
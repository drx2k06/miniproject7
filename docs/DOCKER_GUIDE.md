# Docker Deployment & Viva Defense Guide

## StudentPulse — Student Performance Analytics Dashboard

**Developer:** Daniel Richard Xavier  
**Repository:** [https://github.com/drx2k06/miniproject7.git](https://github.com/drx2k06/miniproject7.git)  

---

## 1. Fundamental Docker Concepts (For Viva Preparation)

### 1.1 What is Docker?
Docker is an open-source platform that automates the deployment of applications inside lightweight, portable, self-sufficient containers.

### 1.2 Docker Image vs. Docker Container
- **Docker Image:** A read-only, immutable template containing the application code, runtime libraries, environment configurations, and dependencies. It acts as the blueprint.
- **Docker Container:** A runnable, isolated instance of an image. Multiple containers can run concurrently from the same image without filesystem interference.

### 1.3 Port Mapping (`-p 8501:8501`)
Containers have an isolated virtual network stack. Port mapping connects a port on the host machine (your physical computer) to a listening port inside the container:
```
Browser Request -> Host Port 8501 -> Docker Bridge -> Container Port 8501 (Streamlit)
```

### 1.4 Dependency Isolation
Traditional Python setups often face conflicting package versions across different projects (dependency hell). Docker packages Python, Pandas, Streamlit, and Plotly in an identical Linux environment regardless of whether the host runs Windows 11, macOS, or Ubuntu.

### 1.5 Non-Root Container Security
By default, Docker processes run as `root` inside the container. StudentPulse creates a dedicated system user `appuser` (UID 1000) and executes Streamlit with restricted privileges, mitigating container breakout risks.

### 1.6 Health Check Mechanism
Streamlit provides a dedicated lightweight health endpoint:
```
http://localhost:8501/_stcore/health
```
The Docker daemon automatically queries this endpoint every 30 seconds. If Streamlit crashes or hangs, the container status transitions to `unhealthy`, allowing container orchestrators to restart it.

---

## 2. Docker CLI Commands

### 2.1 Building the Image
From the project root directory (`miniproject7/`):
```bash
docker build -t studentpulse:latest .
```

### 2.2 Starting the Container
```bash
docker run -d --name studentpulse-app -p 8501:8501 studentpulse:latest
```

### 2.3 Accessing the Application
Open any web browser and navigate to:
```
http://localhost:8501
```

### 2.4 Checking Container Logs
```bash
docker logs -f studentpulse-app
```

### 2.5 Querying the Container Health Status
```bash
docker inspect --format='{{json .State.Health.Status}}' studentpulse-app
```
*Expected output:* `"healthy"`

### 2.6 Stopping and Removing the Container
```bash
docker stop studentpulse-app
docker rm studentpulse-app
```

---

## 3. Docker Compose Instructions

Docker Compose orchestrates multi-parameter container launches using the declarative configuration file `compose.yaml`.

### 3.1 Start Application with Compose
```bash
docker compose up --build -d
```

### 3.2 View Real-time Output
```bash
docker compose logs -f
```

### 3.3 Stop and Clean Up
```bash
docker compose down
```

---

## 4. Troubleshooting & Platform-Specific Notes

### 4.1 If Docker Desktop is Not Installed
1. Download **Docker Desktop** from [https://www.docker.com/products/docker-desktop/](https://www.docker.com/products/docker-desktop/).
2. On Windows, ensure **WSL 2 (Windows Subsystem for Linux)** is enabled.
3. Install Docker Desktop, reboot if prompted, and ensure the Docker Desktop engine icon shows "Engine running".

### 4.2 If Docker Desktop is Installed but Not Running
1. Launch "Docker Desktop" from the Windows Start menu.
2. Wait until the status in the bottom-left corner turns green ("Docker Desktop running").
3. Re-run:
   ```powershell
   docker --version
   docker ps
   ```

### 4.3 Running Without Docker (Local Python Fallback)
If presenting on a computer where Docker is unavailable, the application can be run locally using Python:
```bash
pip install -r requirements.txt
streamlit run app.py
```

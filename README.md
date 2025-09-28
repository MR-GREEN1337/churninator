# Churninator

**Autonomous AI Mystery Shopper for SaaS**

![Dashboard](assets/Dashboard.png)
![Agent](assets/Agent.png)

---

## 🚀 Project Overview

Churninator is an open-source, AI-powered platform that autonomously analyzes the signup and onboarding experience of any web application. Acting as a "mystery shopper," it identifies UX friction points, conversion killers, and usability issues, then generates a detailed, interactive report for product teams.

---

## 🏗️ System Architecture

Churninator is a multi-component, cloud-native platform composed of three main layers:

### 1. The Forge (`forge/`)
**Role:** AI Workshop & ML Pipeline
**Function:** Contains scripts for the two-stage AGUVIS fine-tuning methodology:
- **Stage 1: Grounding**
- **Stage 2: Reasoning**

Designed for full-scale training on remote cloud GPUs (e.g., Vast.ai).

---

### 2. Backend (`backend/`)
**Role:** Mission Control & Production Engine

**Sub-components:**
- **API / Control Plane (`backend/api/`)**: FastAPI server handling user requests and job queuing via Redis.
- **Agent Worker (`backend/worker/`)**: Scalable Celery workers running Playwright in virtual displays (Xvfb) for autonomous browsing tasks.
- **Inference Server (`backend/inference/`)**: Hosts the fine-tuned Churninator model (e.g., via vLLM), acting as the brain for workers.

---

### 3. Frontend (`web/`)
**Role:** Observatory & Executive Dashboard
**Function:** Next.js application featuring a live-view dashboard:
- WebSockets for streaming logs and agent "thoughts"
- MJPEG streaming for browser views
- Interactive UX issue reporting

---

## ⚡ User Experience

1. Submit a target URL and task through the frontend.
2. The API queues the job for processing.
3. A Worker executes the task in a sandboxed browser environment, streaming its actions and insights in real-time to the frontend.
4. A detailed report is generated summarizing UX issues, friction points, and actionable recommendations.

---

## 🛠️ Technologies

- **Backend:** Python, FastAPI, Celery, Redis, PostgreSQL
- **Frontend:** Next.js, TypeScript, WebSockets, MJPEG streaming
- **AI/ML:** PyTorch, vLLM, AGUVIS fine-tuning
- **Deployment:** Docker, Cloud GPUs (Vast.ai compatible)

---

## 📂 Repository Structure

```

forge/       # AI model training pipeline
backend/     # API, workers, inference server
web/         # Next.js frontend dashboard
docker/      # Dockerfiles for deployment
eval/        # Evaluation scripts
train/       # Training datasets & scripts
utils/       # Helper modules
notebooks/   # Experiments & analysis

```

---

## 💡 Usage

### 1. Backend

```bash
cd backend
docker build -f Dockerfile.api -t churninator-api .
docker run -p 8000:8000 churninator-api
```

### 2. Worker

```bash
cd backend/worker
docker build -f Dockerfile.worker -t churninator-worker .
docker run -e REDIS_URL=redis://... churninator-worker
```

### 3. Frontend

```bash
cd web
npm install
npm run dev
```

---

## 📜 License

MIT License

---

## 👏 Contributions

Contributions are welcome! Please open issues or pull requests to improve the platform.

---

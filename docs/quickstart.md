# Quickstart Guide — FloodTwin Responder

Get FloodTwin Responder up and running locally or in containerized mode within 5 minutes.

## 1. Prerequisites
- Python 3.11+
- Node.js 18+ and npm
- (Optional) Docker and Docker Compose

## 2. Local Setup (Zero-Docker)

### Step 1: Clone and Enter Directory
```bash
git clone https://github.com/vijaymahes9080/FloodTwin-Responder.git
cd FloodTwin-Responder
```

### Step 2: Install Backend Dependencies & Seed Testbed
```bash
pip install -r requirements.txt
python scripts/seed_data.py
```

### Step 3: Run Test Suite & Benchmark Evaluation
```bash
pytest tests/ -v
python benchmarks/run_benchmarks.py
```

### Step 4: Start FastAPI Backend Service
```bash
uvicorn backend.app.main:app --reload --host 127.0.0.1 --port 8000
```
- Interactive API Swagger Documentation: `http://127.0.0.1:8000/docs`
- Health Check: `http://127.0.0.1:8000/health`

### Step 5: Start React Frontend Dashboard
In a separate terminal:
```bash
cd frontend
npm install
npm run dev
```
Open `http://localhost:5173` in your browser.

---

## 3. Docker Compose Deployment

To launch the full containerized stack (FastAPI, React Frontend, PostGIS, Redis, n8n):
```bash
docker-compose up -d --build
```
- Frontend Dashboard: `http://localhost:5173`
- Backend REST API: `http://localhost:8000/docs`
- n8n Automation Engine: `http://localhost:5678`

---

## 4. Live Terminal Demo Walkthrough
Run the automated end-to-end disaster scenario verification:
```bash
python scripts/run_demo.py
```
This executes report ingestion, coordinate validation, PII scrubbing, explainable risk scoring, spatial asset prioritization, RAG citation retrieval, Bounded Agent brief generation, human commander authorization, and Merkle audit log verification.

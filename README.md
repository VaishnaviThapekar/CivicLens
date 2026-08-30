# CivicLens — AI-Powered Civic Intelligence Platform

CivicLens turns citizen reports into verified, prioritized, intelligently routed civic actions—and verifies whether the reported problem was actually solved using computer vision and geospatial AI.

---

## 🌟 5 Core AI Capabilities

1. **👁️ Multimodal Computer Vision**: Detects potholes, garbage dumps, clogged storm drains, and broken streetlights directly from photos with dimension estimation and safety risk scoring.
2. **🗣️ Multilingual NLP**: Speech-to-text and intent parsing supporting **Marathi** (*"इथे रस्त्यावर खूप मोठा खड्डा आहे"*), **Hindi** (*"यहाँ सड़क पूरी तरह टूट गई है"*), and **English**.
3. **📍 Spatial Incident Clustering**: Merges 47 independent citizen reports within a 500m radius into a single master incident (`#CI-291`) to uncover root infrastructure failures (e.g., storm drain capacity failure).
4. **🔎 Closed-Loop Resolution Verification**: Compares original complaint photo (**BEFORE**) against officer resolution evidence (**AFTER**) using SSIM and visual feature matching to independently verify repair completion and catch fake/recycled image uploads.
5. **📊 Predictive Civic Intelligence**: Correlates weather forecasts with historical complaint velocity to issue early warnings (e.g., monsoon waterlogging predictions in Zone 4).

---

## 🚀 Quick Start Guide

### 1. Run FastAPI Backend
```bash
cd backend
python -m pip install -r requirements.txt
python run.py
```
- **Backend Server**: `http://localhost:8000`
- **Interactive Swagger Docs**: `http://localhost:8000/docs`

### 2. Run Automated Pytest Suite
```bash
cd backend
python -m pytest
```

### 3. Run Next.js Frontend
```bash
cd frontend
npm install
npm run dev
```
- **Frontend App**: `http://localhost:3000`

---

## 🏗️ Monorepo Architecture

```
civiclens/
├── backend/
│   ├── app/
│   │   ├── main.py                # FastAPI entry point
│   │   ├── models/schemas.py      # Pydantic data contracts
│   │   ├── db/store.py            # Pre-populated mock database
│   │   ├── services/
│   │   │   ├── ai_vision.py       # Computer Vision & Resolution Verification
│   │   │   ├── spatial_cluster.py # Haversine spatial clustering engine
│   │   │   ├── nlp_routing.py     # Multilingual NLP intent & dept router
│   │   │   └── predictive_ai.py   # Historical risk forecaster
│   │   └── routes/
│   │       ├── complaints.py      # Multimodal complaint API
│   │       ├── verification.py    # Resolution verification API
│   │       ├── officer.py         # Command Center queue API
│   │       └── intelligence.py    # Wards, heatmaps & clusters API
│   └── tests/                     # 9/9 Pytest test suite
└── frontend/
    ├── app/
    │   ├── page.tsx               # Landing Page & 5 AI Capabilities
    │   ├── citizen/page.tsx       # Citizen Report Portal & Voice Input
    │   ├── officer/page.tsx       # Command Center & AI Verification Inspector
    │   ├── map/page.tsx           # City Intelligence Map & Heatmap
    │   └── analytics/page.tsx     # Predictive Civic Risk Dashboard
    └── lib/api.ts                 # Backend API client
```

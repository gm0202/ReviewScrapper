# PulseGen AI - Agentic App Review Trend Analyzer

## 🚀 Overview
**PulseGen AI** is a full-stack web application that empowers product teams to instantly analyze Google Play Store reviews. It uses **Agentic AI (Llama 3.1)** to extract specific complaints, deduplicate them using semantic embeddings, and detect emerging trends and spikes in user feedback.

## ✨ Key Features
*   **Search & Scrape**: Input any Android App Name (e.g., "Swiggy", "Instagram") to fetch real-time reviews.
*   **Agentic Extraction**: Uses Groq (Llama 3.1-70b) to label issues intelligently (e.g., "Late delivery" instead of just "bad service").
*   **Trend Detection**:
    *   ⚡ **New Topics**: Identifies complaints that appeared today but never before.
    *   🔥 **Spikes**: Detects issues with >2x volume increase.
*   **AI Insights**: Generates a natural language summary of the analysis.
*   **Visualization**: Interactive charts and data tables.

## 🛠️ Tech Stack
### Backend (Railway)
*   **FastAPI** (Python 3.9+)
*   **BS4 / Google-Play-Scraper**
*   **LangChain + Groq** (Llama 3.1)
*   **Sentence-Transformers** (Deduplication)
*   **Pandas** (Analytics)

### Frontend (Vercel)
*   **Next.js 14** (App Router)
*   **Tailwind CSS**
*   **Recharts**
*   **Axios**

## 🏃 Run Locally

### Prerequisites
*   Python 3.9+
*   Node.js 18+
*   Groq API Key

### 1. Setup Backend
```bash
cd backend
pip install -r requirements.txt

# Create .env
echo "GROQ_API_KEY=gsk_..." > .env

# Run Server
uvicorn main:app --reload
```
*Backend runs on `http://localhost:8000`*

### 2. Setup Frontend
```bash
cd frontend
npm install
npm run dev
```
*Frontend runs on `http://localhost:3000`*

## 🧪 Testing (Mock Mode)
To save API tokens during UI testing:
1.  Enter **"TEST"** as the App Name in the dashboard.
2.  Click **Analyze**.
3.  The system will return instant mock data.

## 📦 Deployment

### Backend (Railway)
1.  Push code to GitHub.
2.  Connect Repo to Railway.
3.  Set Root Directory to `/backend`.
4.  Add `GROQ_API_KEY` in Railway Variables.
5.  Railway auto-detects `Procfile`.

### Frontend (Vercel)
1.  Connect Repo to Vercel.
2.  Set Root Directory to `/frontend`.
3.  Deploy!

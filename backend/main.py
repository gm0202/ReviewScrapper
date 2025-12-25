from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Any
import uvicorn
import os

# Internal modules
import scraper
import agent
import analyzer

app = FastAPI(title="PulseGen - AI App Review Analyzer")

# CORS (Allow Frontend)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # In production specific domains
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class AnalyzeRequest(BaseModel):
    app_name: str
    dates: List[str] # e.g. ["2025-01-01", "2025-01-02"]

@app.get("/")
def health_check():
    return {"status": "ok", "service": "PulseGen Backend"}

@app.post("/analyze")
async def analyze_reviews(req: AnalyzeRequest):
    print(f"[API] Received analysis request for '{req.app_name}' on {req.dates}")
    
    # 1. Mock Mode
    if req.app_name == "TEST":
        return {
            "topics": ["Delivery delay", "Cold food", "App crashes"],
            "trend": {
                "Delivery delay": [12, 8],
                "Cold food": [5, 1],
                "App crashes": [2, 4]
            },
            "dates": req.dates if req.dates else ["2025-01-01", "2025-01-02"],
            "newTopics": ["Stories not uploading"],
            "spikes": ["App crashes"],
            "insights": "Users recently experienced more app crashes (spike detected), increasing by 200%. 'Stories not uploading' emerged as a new issue on the last day."
        }

    # 2. Search App
    app_id = scraper.search_app_id(req.app_name)
    if not app_id:
        raise HTTPException(status_code=404, detail=f"App '{req.app_name}' not found on Play Store.")
    
    # 3. Scrape & Agent Loop
    daily_stats_map = {}
    
    for date_str in req.dates:
        # Fetch for this specific day
        # We assume fetch_reviews_for_date_range works for single day if start=end
        reviews = scraper.fetch_reviews_for_date_range(app_id, date_str, date_str)
        
        if not reviews:
            daily_stats_map[date_str] = {}
            continue
            
        # Process with Agent
        # daily_topics = { "Topic A": 5, ... }
        daily_topics = agent.process_daily_batch(date_str, reviews)
        daily_stats_map[date_str] = daily_topics

    # 4. Analyze Trends
    # Returns { "trend_matrix": ..., "new_topics": ..., "spikes": ..., "dates": ... }
    analysis_result = analyzer.analyze_trends(daily_stats_map)
    
    # 5. Generate Insights
    # We pass the sorted trend matrix (top 5 are usually enough for insights contextualization)
    insight_text = agent.generate_insights_for_period(
        analysis_result["trend_matrix"],
        analysis_result["new_topics"],
        analysis_result["spikes"]
    )
    
    # 6. Final Response
    return {
        "topics": list(analysis_result["trend_matrix"].keys()), # All topics sorted by volume
        "trend": analysis_result["trend_matrix"],               # {Topic: [d1, d2, ...]}
        "dates": analysis_result["dates"],                      # [d1, d2, ...]
        "newTopics": analysis_result["new_topics"],
        "spikes": analysis_result["spikes"],
        "insights": insight_text
    }

if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)

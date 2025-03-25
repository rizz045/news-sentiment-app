# api.py (FastAPI backend)
from fastapi import FastAPI, Query, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from utils import fetch_news_articles, generate_report, generate_tts
from typing import Optional
import os

app = FastAPI()

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/scrape_news")
async def scrape_news(company: str = Query(..., description="Company name to search"), 
                     api_key: str = Query(..., description="NewsAPI key")):
    try:
        news_data = fetch_news_articles(company, api_key)
        if not news_data:
            raise HTTPException(status_code=404, detail="No news found for this company")
        return {"company": company, "articles": news_data}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/sentiment_analysis")
async def sentiment_analysis(company: str = Query(..., description="Company name to analyze"),
                            api_key: str = Query(..., description="NewsAPI key")):
    try:
        news_data = fetch_news_articles(company, api_key)
        if not news_data:
            raise HTTPException(status_code=404, detail="No news found for this company")
        
        report = generate_report(news_data, company)
        return {
            "company": company,
            "sentiment_distribution": report["Comparative Sentiment Score"]["Sentiment Distribution"],
            "final_analysis": report["Final Sentiment Analysis"]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/tts_hindi")
async def text_to_speech(company: str = Query(..., description="Company name"),
                         api_key: str = Query(..., description="NewsAPI key")):
    try:
        news_data = fetch_news_articles(company, api_key)
        if not news_data:
            raise HTTPException(status_code=404, detail="No news found for this company")
        
        audio_file = generate_tts(news_data, company)
        with open(audio_file, "rb") as f:
            audio_bytes = f.read()
        os.remove(audio_file)  # Clean up
        
        return {
            "company": company,
            "audio": base64.b64encode(audio_bytes).decode("utf-8"),
            "filename": f"{company}_summary.mp3"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
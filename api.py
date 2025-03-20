from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from utils import fetch_news_articles, analyze_sentiment, generate_tts

app = FastAPI()

class CompanyRequest(BaseModel):
    company_name: str

@app.post("/analyze-news")
def analyze_news(request: CompanyRequest):
    company_name = request.company_name
    articles = fetch_news_articles(company_name)
    
    if not articles:
        raise HTTPException(status_code=404, detail="No news articles found.")
    
    # Perform sentiment analysis
    for article in articles:
        article["sentiment"] = analyze_sentiment(article["summary"])
    
    # Generate TTS
    tts_file = generate_tts(articles, company_name)
    
    return {
        "company": company_name,
        "articles": articles,
        "tts_file": tts_file
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
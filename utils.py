import requests
from bs4 import BeautifulSoup
from textblob import TextBlob
from gtts import gTTS
import os

def fetch_news_articles(company_name, api_key):
    """
    Fetch news articles related to the company using NewsAPI.
    
    :param company_name: Name of the company to search for.
    :param api_key: Your NewsAPI API key.
    :return: List of news articles.
    """
    # NewsAPI endpoint for fetching everything
    url = "https://newsapi.org/v2/everything"
    
    # Parameters for the API request
    params = {
        "q": company_name,  # Search query
        "apiKey": api_key,  # Your API key
        "language": "en",   # Language of the articles
        "sortBy": "publishedAt",  # Sort by publication date
        "pageSize": 10  # Number of articles to fetch
    }
    
    try:
        # Make the API request
        response = requests.get(url, params=params)
        response.raise_for_status()  # Raise an error for bad status codes
        
        # Parse the JSON response
        data = response.json()
        
        # Extract relevant information from the response
        articles = []
        for article in data.get("articles", []):
            articles.append({
                "title": article.get("title", "No title"),
                "summary": article.get("description", "No summary"),
                "url": article.get("url", "#")
            })
        
        return articles
    
    except requests.exceptions.RequestException as e:
        print(f"Error fetching news articles: {e}")
        return []


def analyze_sentiment(text):
    """
    Analyze the sentiment of a given text using TextBlob.
    """
    analysis = TextBlob(text)
    if analysis.sentiment.polarity > 0:
        return "Positive"
    elif analysis.sentiment.polarity < 0:
        return "Negative"
    else:
        return "Neutral"


def generate_tts(articles, company_name):
    """
    Generate Hindi TTS for the summarized content.
    """
    summary = f"{company_name} के समाचार कवरेज का विश्लेषण:\n"
    for i, article in enumerate(articles):
        summary += f"लेख {i + 1}: {article['title']}\n"
    
    tts = gTTS(summary, lang='hi')
    tts_file = f"{company_name}_summary.mp3"
    tts.save(tts_file)
    return tts_file
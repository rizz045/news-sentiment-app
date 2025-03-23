import requests
from bs4 import BeautifulSoup
from textblob import TextBlob
from gtts import gTTS
import os
from collections import defaultdict
import spacy
import re

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





def analyze_sentiment(text):
    """
    Analyze the sentiment of a given text using TextBlob.
    Returns 'Positive', 'Negative', or 'Neutral'.
    """
    analysis = TextBlob(text)
    if analysis.sentiment.polarity > 0:
        return "Positive"
    elif analysis.sentiment.polarity < 0:
        return "Negative"
    else:
        return "Neutral"


# Load the spaCy model (install it first: pip install spacy && python -m spacy download en_core_web_sm)
nlp = spacy.load("en_core_web_sm")

def extract_topics(text, company):
    """
    Extract topics dynamically using NLP (Named Entity Recognition and POS tagging).
    """
    topics = set()  # Use a set to avoid duplicates
    doc = nlp(text)

    # Extract entities (e.g., organizations, products, locations)
    for ent in doc.ents:
        if ent.label_ in ["ORG", "PRODUCT", "GPE"]:  # ORG = Organization, PRODUCT = Product, GPE = Location
            topics.add(ent.text)

    # Extract nouns and noun phrases (common topics)
    for chunk in doc.noun_chunks:
        if chunk.root.pos_ == "NOUN":  # Focus on nouns
            topics.add(chunk.text)

    # Add the company name as a topic
    topics.add(company)

    # Filter out generic words (optional)
    generic_words = {"company", "news", "article", "report", "year", "time", "day"}
    topics = {topic for topic in topics if topic.lower() not in generic_words}

    return list(topics)

def identify_company(news_data):
    """
    Identify the company name from the news data.
    """
    # company_keywords = ["tesla", "apple", "microsoft", "google", "amazon", "meta", "nvidia"]
    company_keywords = [
    "Apple",
    "Microsoft",
    "Google",
    "Amazon",
    "Meta",
    "Tesla",
    "Samsung",
    "Sony",
    "Intel",
    "IBM",
    "NVIDIA",
    "Tata Group",
    "Reliance Industries",
    "Infosys",
    "Wipro",
    "HCL Technologies",
    "Adani Group",
    "Larsen And Toubro",
    "Mahindra",
    "Hindustan Unilever",
    "Flipkart",
    "BYJU'S",
    "Ola Cabs",
    "Paytm",
    "Berkshire Hathaway",
    "JPMorgan Chase",
    "Goldman Sachs",
    "Visa",
    "Mastercard",
    "Coca-Cola",
    "PepsiCo",
    "McDonald's",
    "Starbucks",
    "Nestlé",
    "Unilever",
    "Nike",
    "Adidas",
    "Zara",
    "Louis Vuitton (LVMH)",
    "Mercedes-Benz",
    "BMW",
    "Toyota",
    "Ford",
    "Hyundai",
    "Netflix",
    "Disney",
    "YouTube",
    "WhatsApp",
    "Adobe",
    "Oracle"
]
    for article in news_data:
        text = article["title"] + " " + article["summary"]
        for keyword in company_keywords:
            if keyword in text.lower():
                return keyword.capitalize()
    return "Unknown Company"

def generate_report(news_data):
    """
    Generate a structured report from the provided news data.
    """
    if not news_data:
        return {"error": "No news data provided."}

    # Identify the company dynamically
    company = identify_company(news_data)
    articles = []
    sentiment_distribution = defaultdict(int)
    all_topics = defaultdict(int)
    unique_topics_per_article = []

    for article in news_data:
        title = article["title"]
        summary = article["summary"]
        sentiment = analyze_sentiment(summary)
        topics = extract_topics(summary, company)  # Use the new extract_topics function

        # Update sentiment distribution
        sentiment_distribution[sentiment] += 1

        # Update topic frequency
        for topic in topics:
            all_topics[topic] += 1

        # Store article details
        articles.append({
            "Title": title,
            "Summary": summary,
            "Sentiment": sentiment,
            "Topics": topics
        })

        # Store unique topics per article
        unique_topics_per_article.append(set(topics))

    # Find common and unique topics
    common_topics = set.intersection(*unique_topics_per_article) if unique_topics_per_article else set()
    unique_topics = []
    for i, topics in enumerate(unique_topics_per_article):
        unique_topics.append({
            f"Unique topics in Article {i + 1}": list(topics - common_topics)
        })

    # Generate comparative sentiment analysis
    comparative_sentiment_score = {
        "Sentiment Distribution": dict(sentiment_distribution),
        "Coverage Differences": [],
        "Topic Overlap": {
            "Common Topics": list(common_topics),
            "Unique Topics": unique_topics
        }
    }

    # Add comparisons and impacts if there are at least 2 articles
    if len(articles) >= 2:
        for i in range(len(articles) - 1):
            comparison = f"Article {i+1} highlights {articles[i]['Topics'][0] if articles[i]['Topics'] else 'general news'}, while Article {i+2} discusses {articles[i+1]['Topics'][0] if articles[i+1]['Topics'] else 'general news'}."
            impact = f"The first article may influence {articles[i]['Sentiment']} sentiment, while the second raises {articles[i+1]['Sentiment']} concerns."
            comparative_sentiment_score["Coverage Differences"].append({
                "Comparison": comparison,
                "Impact": impact
            })

    # Final sentiment analysis
    final_sentiment = "Positive" if sentiment_distribution["Positive"] > sentiment_distribution["Negative"] else "Negative"
    final_sentiment_analysis = f"{company}'s latest news coverage is mostly {final_sentiment}. Potential stock growth expected."

    # Construct the final report
    report = {
        "Company": company,
        "Articles": articles,
        "Comparative Sentiment Score": comparative_sentiment_score,
        "Final Sentiment Analysis": final_sentiment_analysis,
        "Audio": "[Play Hindi Speech]"
    }

    return report
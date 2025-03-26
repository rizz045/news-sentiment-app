import requests
from bs4 import BeautifulSoup
from textblob import TextBlob
from gtts import gTTS
import os
from collections import defaultdict
import spacy
import re
import requests


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
        # print(data)
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


from textblob import TextBlob

def analyze_sentiment(text):
    if not text or text.strip() == "":  # Check if text is empty or only spaces
        return "Neutral"

    analysis = TextBlob(text)
    polarity = analysis.sentiment.polarity

    if polarity > 0:
        return "Positive"
    elif polarity < 0:
        return "Negative"
    else:
        return "Neutral"


def generate_tts(articles, company_name):
    """
    Generate Hindi TTS that includes both titles and summaries
    """
    summary = f"{company_name} के समाचार कवरेज का विश्लेषण:\n\n"
    
    for i, article in enumerate(articles):
        # Get title (handling both 'Title' and 'title' keys)
        title = article.get('Title') or article.get('title', 'No title')
        # Get summary (handling both 'Summary' and 'summary' keys)
        article_summary = article.get('Summary') or article.get('summary', 'No summary available')
        
        summary += f"लेख {i + 1}: {title}\n"
        summary += f"सारांश: {article_summary}\n\n"
    
    tts = gTTS(text=summary, lang='hi', slow=False)
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


def extract_topics(text, company):
    """
    Extract topics dynamically using NLP (Named Entity Recognition and POS tagging).
    """
    # Load the spaCy model (install it first: pip install spacy && python -m spacy download en_core_web_sm)
    nlp = spacy.load("en_core_web_sm")

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
    # topics.add(company)

    # Filter out generic words (optional)
    generic_words = {"company", "news", "article", "report", "year", "time", "day"}
    topics = {topic for topic in topics if topic.lower() not in generic_words}

    return list(topics)

###

def generate_report(news_data, company_name):
    if not news_data:
        return {"error": "No news data provided."}

    company = company_name
    articles = []
    sentiment_distribution = defaultdict(int)
    all_topics = defaultdict(int)
    unique_topics_per_article = []

    for article in news_data:
        title = article.get("title", "No title")
        summary = article.get("summary", "No summary")
        url = article.get("url", "#")  # URL with fallback
        sentiment = analyze_sentiment(summary)
        topics = extract_topics(summary, company) or ["General news"]  # Fallback for empty topics

        sentiment_distribution[sentiment] += 1

        articles.append({
            "title": title,  # Lowercase key
            "Title": title,  # Keep both for compatibility
            "summary": summary,
            "Summary": summary,
            "Sentiment": sentiment,
            "Topics": topics,
            "url": url
        })
        unique_topics_per_article.append(set(topics))

    # Generate comparative analysis
    comparative_score = {
        "Sentiment Distribution": dict(sentiment_distribution),
        "Coverage Differences": generate_coverage_differences(articles),
        "Topic Overlap": generate_topic_analysis(unique_topics_per_article)
    }

    # Generate final conclusion
    conclusion = generate_conclusion(company, sentiment_distribution)

    return {
        "Company": company,
        "Articles": articles,
        "Comparative Sentiment Score": comparative_score,
        "Final Sentiment Analysis": conclusion,
        "Audio": f"{company_name}_summary.mp3"
    }

# New helper functions
def generate_coverage_differences(articles):
    differences = []
    for i in range(len(articles)-1):
        art1 = articles[i]
        art2 = articles[i+1]
        comparison = (f"Article {i+1} focuses on {art1['Topics'][0] if art1['Topics'] else 'general topics'}, "
                    f"while Article {i+2} discusses {art2['Topics'][0] if art2['Topics'] else 'different topics'}.")
        impact = f"Sentiment shifts from {art1['Sentiment']} to {art2['Sentiment']}."
        differences.append({"Comparison": comparison, "Impact": impact})
    return differences

def generate_topic_analysis(unique_topics):
    common = set.intersection(*unique_topics) if unique_topics else set()
    unique = [{"Article "+str(i+1): list(t-set(common))} 
             for i,t in enumerate(unique_topics)]
    return {"Common Topics": list(common), "Unique Topics": unique}

def generate_conclusion(company, sentiment_dist):
    pos = sentiment_dist.get("Positive", 0)
    neg = sentiment_dist.get("Negative", 0)
    
    if pos > neg:
        return f"{company}'s news is mostly positive ({pos} vs {neg} negative). Potential stock growth."
    elif neg > pos:
        return f"{company}'s news is mostly negative ({neg} vs {pos} positive). Potential stock decline."
    return f"{company} has balanced coverage ({pos} positive, {neg} negative). Stock may remain stable."
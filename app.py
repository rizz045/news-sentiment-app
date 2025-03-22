# import streamlit as st
# import requests

# # NewsAPI key (replace with your actual key)
# NEWS_API_KEY = "0b0dbfef2952432ca910d149147dbc4a"

# def fetch_news_articles(company_name, api_key):
#     """
#     Fetch news articles related to the company using NewsAPI.
    
#     :param company_name: Name of the company to search for.
#     :param api_key: Your NewsAPI API key.
#     :return: List of news articles.
#     """
#     # NewsAPI endpoint for fetching everything
#     url = "https://newsapi.org/v2/everything"
    
#     # Parameters for the API request
#     params = {
#         "q": company_name,  # Search query
#         "apiKey": api_key,  # Your API key
#         "language": "en",   # Language of the articles
#         "sortBy": "publishedAt",  # Sort by publication date
#         "pageSize": 10  # Number of articles to fetch
#     }
    
#     try:
#         # Make the API request
#         response = requests.get(url, params=params)
#         response.raise_for_status()  # Raise an error for bad status codes
        
#         # Parse the JSON response
#         data = response.json()
        
#         # Extract relevant information from the response
#         articles = []
#         for article in data.get("articles", []):
#             articles.append({
#                 "title": article.get("title", "No title"),
#                 "summary": article.get("description", "No summary"),
#                 "url": article.get("url", "#")
#             })
        
#         return articles
    
#     except requests.exceptions.RequestException as e:
#         st.error(f"Error fetching news articles: {e}")
#         return []

# def main():
#     st.title("Company News Sentiment Analysis")
    
#     # Input: Company name
#     company_name = st.text_input("Enter the name of the company:")
    
#     if st.button("Analyze News"):
#         if company_name:
#             # Fetch news articles using the NewsAPI
#             articles = fetch_news_articles(company_name, NEWS_API_KEY)
            
#             if articles:
#                 # Display articles
#                 st.subheader(f"News Articles for {company_name}")
#                 for article in articles:
#                     st.write(f"**Title:** {article['title']}")
#                     st.write(f"**Summary:** {article['summary']}")
#                     st.write(f"**URL:** [Read more]({article['url']})")
#                     st.write("---")
#             else:
#                 st.warning("No news articles found for the given company.")
#         else:
#             st.warning("Please enter a company name.")

# if __name__ == "__main__":
#     main()


import streamlit as st
import requests
from textblob import TextBlob
from transformers import pipeline

# NewsAPI key (replace with your actual key)
NEWS_API_KEY = "0b0dbfef2952432ca910d149147dbc4a"

# Load summarization pipeline
summarizer = pipeline("summarization")

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
        "pageSize": 5  # Number of articles to fetch
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
                "content": article.get("content", "No content"),
                "url": article.get("url", "#")
            })
        
        return articles
    
    except requests.exceptions.RequestException as e:
        st.error(f"Error fetching news articles: {e}")
        return []

def summarize_text(text, max_length=130, min_length=30):
    """
    Summarize the given text using a pre-trained summarization model.
    
    :param text: Text to summarize.
    :param max_length: Maximum length of the summary.
    :param min_length: Minimum length of the summary.
    :return: Summarized text.
    """
    if not text or text == "No content":
        return "No content available for summarization."
    
    # Summarize the text
    summary = summarizer(text, max_length=max_length, min_length=min_length, do_sample=False)
    return summary[0]['summary_text']

def analyze_sentiment(text):
    """
    Analyze the sentiment of the given text using TextBlob.
    
    :param text: Text to analyze.
    :return: Sentiment polarity (-1 to 1).
    """
    analysis = TextBlob(text)
    return analysis.sentiment.polarity

def generate_inference(summary, sentiment):
    """
    Generate meaningful inferences based on the summary and sentiment.
    
    :param summary: Summarized text.
    :param sentiment: Sentiment polarity.
    :return: Inference as a string.
    """
    if sentiment > 0.2:
        return "The news is generally positive. This could indicate favorable developments or growth for the company."
    elif sentiment < -0.2:
        return "The news is generally negative. This could indicate challenges or setbacks for the company."
    else:
        return "The news is neutral. There may not be any significant developments at the moment."

def main():
    st.title("Company News Sentiment Analysis and Summarization")
    
    # Input: Company
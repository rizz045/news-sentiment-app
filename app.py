# app.py (Streamlit frontend)
import streamlit as st
import requests
from utils import generate_report, generate_tts
import base64

# API configuration (will point to FastAPI backend)
API_URL = "http://localhost:8000"  # Change for deployment

def main():
    st.title("Company News Sentiment Analyzer")
    
    # Input section
    company_name = st.text_input("Enter company name (e.g., Tesla, Apple):")
    api_key = st.text_input("Enter your NewsAPI key:", type="password")
    
    if st.button("Analyze News"):
        if not company_name or not api_key:
            st.warning("Please enter both company name and API key")
            return
            
        with st.spinner("Fetching and analyzing news..."):
            # Call backend API or use local functions
            try:
                # For demo, using local functions directly
                from utils import fetch_news_articles
                news_data = fetch_news_articles(company_name, api_key)
                
                if not news_data:
                    st.error("No news found for this company")
                    return
                
                # Generate report
                report = generate_report(news_data, company_name)
                
                # Display results
                st.header(f"News Analysis for {company_name}")
                
                # 1. Display articles
                st.subheader("News Articles")
                for article in report["Articles"]:
                    with st.expander(article["Title"]):
                        st.write(article["Summary"])
                        st.write(f"Sentiment: {article['Sentiment']}")
                        st.write(f"Topics: {', '.join(article['Topics'])}")
                
                # 2. Sentiment visualization
                st.subheader("Sentiment Analysis")
                sentiment_data = report["Comparative Sentiment Score"]["Sentiment Distribution"]
                st.bar_chart(sentiment_data)
                
                # 3. Final analysis
                st.subheader("Overall Analysis")
                st.write(report["Final Sentiment Analysis"])
                
                # 4. Audio download
                st.subheader("Hindi Summary")
                audio_file = generate_tts(news_data, company_name)
                with open(audio_file, "rb") as f:
                    audio_bytes = f.read()
                st.audio(audio_bytes, format="audio/mp3")
                
                st.download_button(
                    label="Download Hindi Summary",
                    data=audio_bytes,
                    file_name=f"{company_name}_summary.mp3",
                    mime="audio/mp3"
                )
                
            except Exception as e:
                st.error(f"An error occurred: {str(e)}")

if __name__ == "__main__":
    main()
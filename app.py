# app.py - Streamlit App for Company News Sentiment Analysis
import streamlit as st
from utils import fetch_news_articles, generate_report, generate_tts
import os
import base64

def main():
    st.title("📰 Company News Sentiment Analyzer")
    st.markdown("Analyze news sentiment and get a Hindi audio summary for any company.")
    
    # Input section with improved UI
    col1, col2 = st.columns(2)
    with col1:
        company_name = st.text_input("Enter company name:", placeholder="Tesla, Apple, etc.")
    with col2:
        # Use Streamlit Secrets if available, otherwise ask for input
        if 'NEWSAPI_KEY' in st.secrets:
            api_key = st.secrets['NEWSAPI_KEY']
            st.info("Using secured NewsAPI key")
        else:
            api_key = st.text_input("Enter NewsAPI key:", type="password", 
                                  help="Get a free key from newsapi.org")
    
    if st.button("🚀 Analyze News", type="primary"):
        if not company_name:
            st.warning("Please enter a company name")
            return
            
        if not api_key:
            st.error("API key is required. Get one from newsapi.org")
            return
            
        with st.spinner("🔍 Fetching and analyzing news..."):
            try:
                # Fetch news articles
                news_data = fetch_news_articles(company_name, api_key)
                
                if not news_data:
                    st.error(f"No news found for {company_name}. Try a different company.")
                    return
                
                # Generate report
                report = generate_report(news_data, company_name)
                
                # Display results in expandable sections
                st.header(f"📊 Analysis for {company_name}")
                
                # 1. News Articles Section
                with st.expander("📰 News Articles", expanded=True):
                    for i, article in enumerate(report["Articles"]):
                        st.subheader(f"Article {i+1}: {article['Title']}")
                        st.caption(f"Sentiment: {article['Sentiment']}")
                        st.write(article["Summary"])
                        st.markdown(f"**Topics:** {', '.join(article['Topics'])}")
                        st.markdown(f"[Read more]({article.get('url', '#')})")
                        st.divider()
                
                # 2. Sentiment Visualization
                with st.expander("📈 Sentiment Analysis", expanded=True):
                    sentiment_data = report["Comparative Sentiment Score"]["Sentiment Distribution"]
                    st.bar_chart(sentiment_data)
                    
                    # Add pie chart for better visualization
                    if sum(sentiment_data.values()) > 0:
                        st.write("### Sentiment Distribution")
                        st.pie_chart(sentiment_data)
                
                # 3. Overall Analysis
                with st.expander("🔍 Overall Insights", expanded=True):
                    st.write(report["Final Sentiment Analysis"])
                    
                    # Show topic overlap if available
                    if "Topic Overlap" in report["Comparative Sentiment Score"]:
                        st.write("### Common Topics Across Articles")
                        st.write(", ".join(report["Comparative Sentiment Score"]["Topic Overlap"]["Common Topics"]))
                
                # 4. Hindi Audio Summary
                with st.expander("🎧 Hindi Audio Summary", expanded=True):
                    try:
                        audio_file = generate_tts(news_data, company_name)
                        with open(audio_file, "rb") as f:
                            audio_bytes = f.read()
                        
                        st.audio(audio_bytes, format="audio/mp3")
                        
                        # Download button with custom styling
                        st.download_button(
                            label="⬇️ Download Hindi Summary",
                            data=audio_bytes,
                            file_name=f"{company_name}_hindi_summary.mp3",
                            mime="audio/mp3",
                            use_container_width=True
                        )
                        
                        # Clean up the audio file
                        os.remove(audio_file)
                    except Exception as e:
                        st.error(f"Failed to generate audio: {str(e)}")
                
            except Exception as e:
                st.error(f"❌ An error occurred: {str(e)}")
                st.error("Please check your API key and try again.")

    # Add footer with instructions
    st.divider()
    st.markdown("""
    ### How to use:
    1. Enter a company name (e.g., Tesla, Apple)
    2. Provide your [NewsAPI](https://newsapi.org) key
    3. Click "Analyze News" to get results
    """)

if __name__ == "__main__":
    main()
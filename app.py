import streamlit as st
from utils import fetch_news_articles, generate_report, generate_tts
import os
import matplotlib.pyplot as plt

def main():
    st.set_page_config(page_title="News Sentiment Analyzer", layout="wide")
    st.title("📰 Company News Sentiment Analyzer")
    
    # Input section
    with st.form(key="analysis_form"):
        company_name = st.text_input("Enter company name:", placeholder="Tesla, Apple, etc.")
        
        if 'NEWSAPI_KEY' in st.secrets:
            api_key = st.secrets['NEWSAPI_KEY']
            st.info("Using secured NewsAPI key")
        else:
            api_key = st.text_input("Enter NewsAPI key:", type="password")
        
        submitted = st.form_submit_button("🚀 Analyze News", type="primary")
    
    if submitted:
        if not company_name:
            st.warning("Please enter a company name")
            return
            
        if not api_key:
            st.error("API key is required")
            return
            
        with st.spinner("🔍 Fetching and analyzing news..."):
            try:
                news_data = fetch_news_articles(company_name, api_key)
                if not news_data:
                    st.error("No news found. Try a different company.")
                    return
                
                report = generate_report(news_data, company_name)
                
                # 1. Overall Summary
                with st.expander("📊 Overall Summary", expanded=True):
                    cols = st.columns(3)
                    sentiment_dist = report['Comparative Sentiment Score']['Sentiment Distribution']
                    cols[0].metric("Positive", sentiment_dist['Positive'])
                    cols[1].metric("Negative", sentiment_dist['Negative'])
                    cols[2].metric("Neutral", sentiment_dist['Neutral'])
                    
                    sentiment = report['Final Sentiment Analysis']
                    if "Positive" in sentiment:
                        st.success(sentiment)
                    elif "Negative" in sentiment:
                        st.error(sentiment)
                    else:
                        st.warning(sentiment)
                
                # 2. Articles Display
                st.header("📰 News Articles")
                for i, article in enumerate(report["Articles"]):
                    with st.expander(f"Article {i+1}: {article['Title']}"):
                        st.caption(f"Sentiment: {article['Sentiment']}")
                        st.write(article["Summary"])
                        
                        if article.get('url') and article['url'] not in ["", "#"]:
                            st.markdown(f"**Read full article:** [Link]({article['url']})")
                        else:
                            st.warning("Original article URL not available")
                        
                        st.markdown("**Topics:** " + ", ".join(article['Topics']))
                
                # 3. Comparative Analysis
                with st.expander("🔍 Comparative Analysis"):
                    # Sentiment Charts
                    fig, ax = plt.subplots(1, 2, figsize=(10,4))
                    
                    # Bar chart
                    ax[0].bar(
                        report['Comparative Sentiment Score']['Sentiment Distribution'].keys(),
                        report['Comparative Sentiment Score']['Sentiment Distribution'].values(),
                        color=['green', 'red', 'orange']
                    )
                    ax[0].set_title("Sentiment Distribution")
                    
                    # Pie chart
                    ax[1].pie(
                        report['Comparative Sentiment Score']['Sentiment Distribution'].values(),
                        labels=report['Comparative Sentiment Score']['Sentiment Distribution'].keys(),
                        autopct='%1.1f%%',
                        colors=['green', 'red', 'orange']
                    )
                    ax[1].set_title("Sentiment Ratio")
                    st.pyplot(fig)
                    
                    # Coverage Differences
                    st.subheader("Coverage Differences")
                    for diff in report['Comparative Sentiment Score']['Coverage Differences']:
                        col1, col2 = st.columns([3,1])
                        col1.write(f"**Comparison:** {diff['Comparison']}")
                        col2.write(f"**Impact:** {diff['Impact']}")
                        st.divider()
                    
                    # Topic Analysis
                    st.subheader("Topic Analysis")
                    st.write("**Common Topics:** " + 
                            ", ".join(report['Comparative Sentiment Score']['Topic Overlap']['Common Topics']))
                    
                    st.write("**Unique Topics:**")
                    for unique in report['Comparative Sentiment Score']['Topic Overlap']['Unique Topics']:
                        for art, topics in unique.items():
                            st.write(f"- {art}: {', '.join(topics)}")
                
                # 4. Audio Summary
                if report.get('Audio'):
                    with st.expander("🎧 Hindi Audio Summary", expanded=False):
                        try:
                            if not os.path.exists(report['Audio']):
                                # Prepare articles data with consistent structure
                                audio_articles = [
                                    {
                                        'Title': article['Title'],
                                       'Summary': article['Summary'][:300] + "..." if len(article['Summary']) > 300 else article['Summary']
                                    } 
                                    for article in report['Articles']
                                ]

                               # Generate new audio file with both titles and summaries
                                audio_file = generate_tts(audio_articles, report['Company'])
                                report['Audio'] = audio_file  # Update report with new file path

                            if os.path.exists(report['Audio']):
                                # Display audio player
                                st.audio(report['Audio'], format='audio/mp3')

                                # Add download button
                                with open(report['Audio'], "rb") as f:
                                    st.download_button(
                                        label="⬇️ Download Full Summary (Hindi)",
                                        data=f,
                                        file_name=f"{report['Company']}_news_summary.mp3",
                                        mime="audio/mp3",
                                        help="Download the Hindi audio summary of all articles"
                                    )

                                # Display what's included in the audio
                                st.caption("This audio summary includes:")
                                st.markdown("""
                                - Company name introduction
                                - All article titles
                                - Summarized content for each article
                                """)

                            else:
                                st.warning("Audio file could not be generated. Please try again.")

                        except Exception as e:
                            st.error(f"Failed to generate audio summary: {str(e)}")
                            st.error("Please check your internet connection and try again.")
                
            except Exception as e:
                st.error(f"Analysis failed: {str(e)}")

if __name__ == "__main__":
    main()
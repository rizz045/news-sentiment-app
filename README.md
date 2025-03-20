# News Sentiment Analysis App

## Overview
This application extracts news articles related to a given company, performs sentiment analysis, conducts comparative analysis, and generates a Hindi text-to-speech (TTS) output.

## Setup
1. Clone the repository:
   ```bash
   git clone https://github.com/rizz045/news-sentiment-app.git

2. Locate the cloned directory:
   ```bash
   cd /c/your_location_address

3. Install Dependencies:
    ```bash
    pip install -r requirements.txt

4. Run the backend API:
    ```bash
    uvicorn api:app --reload

5. Run the Streamlit frontend:
    ```bash
    streamlit run app.py
import streamlit as st
from google_play_scraper import reviews
from transformers import pipeline
import matplotlib.pyplot as plt
import warnings
warnings.filterwarnings("ignore")

st.set_page_config(page_title="Google Play Review Analyzer", layout="centered")
st.title("📱 Google Play App Review Analyzer")
st.write("Enter the App ID (e.g. `com.whatsapp`) to analyze user sentiment and see charts.")

app_id = st.text_input("Google Play App ID", value="com.whatsapp")

if st.button("Analyze"):
    with st.spinner("Fetching and analyzing reviews..."):

        @st.cache_data(show_spinner=False)
        def get_reviews(app_id, count=200):
            result, _ = reviews(app_id, lang='en', country='us', count=count)
            return [r['content'] for r in result]

        @st.cache_resource(show_spinner=False)
        def get_model():
            return pipeline("sentiment-analysis", model="distilbert-base-uncased-finetuned-sst-2-english")

        try:
            review_texts = get_reviews(app_id)
            sentiment_classifier = get_model()
            sentiments = sentiment_classifier(review_texts)

            pos_count = sum(1 for s in sentiments if s['label'] == 'POSITIVE')
            neg_count = len(sentiments) - pos_count
            score = round((pos_count / len(sentiments)) * 10, 2)

            st.success(f"App Sentiment Score: **{score} / 10** based on {len(sentiments)} reviews")

            fig, axs = plt.subplots(1, 2, figsize=(12, 5))

            axs[0].pie([pos_count, neg_count], labels=['Positive', 'Negative'], colors=['#4CAF50', '#F44336'],
                       autopct='%1.1f%%', startangle=140)
            axs[0].set_title('Sentiment Distribution')

            axs[1].bar(['Positive', 'Negative'], [pos_count, neg_count], color=['#4CAF50', '#F44336'])
            axs[1].set_title('Sentiment Count')
            axs[1].set_ylabel('Number of Reviews')

            st.pyplot(fig)

            with st.expander("See some sample reviews"):
                for r in review_texts[:10]:
                    st.markdown(f"- {r}")

        except Exception as e:
            st.error(f"Failed to fetch or analyze reviews: {e}")

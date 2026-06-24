# import os
# import streamlit as st
# import pandas as pd
# import numpy as np
# import re
# from wordcloud import WordCloud
# import plotly.express as px
# from datetime import datetime
# import matplotlib.pyplot as plt
# from transformers import pipeline

# st.set_page_config(page_title="Social Media Intelligence System", layout="wide")

# # =============================================
# # DATASET IMPORT
# # =============================================

# @st.cache_data
# def load_dataset():
#     try:
#         df = pd.read_csv("dataset/cleaned_twitter_data.csv")
#         st.success("✅ Loaded original dataset successfully!")
#         return df
#     except:
#         try:
#             df = pd.read_csv("/home/workdir/attachments/twitter_training_enhanced.csv")
#             st.success("✅ Loaded from attachments folder!")
#             return df
#         except:
#             st.warning("Using Demo Data...")
            
#     # Demo Data
#     np.random.seed(42)
#     df = pd.DataFrame({
#         'tweet_id': range(8000),
#         'entity': np.random.choice(['Borderlands', 'Nvidia', 'Amazon', 'MaddenNFL'], 8000),
#         'sentiment': np.random.choice(['Positive', 'Negative', 'Neutral', 'Irrelevant'], 8000, p=[0.28, 0.30, 0.25, 0.17]),
#         'tweet': [f"Sample tweet about {e} and latest update" for e in np.random.choice(['gaming', 'tech', 'AI'], 8000)],
#         'followers': np.random.randint(1000, 500000, 8000),
#         'likes': np.random.randint(50, 30000, 8000),
#         'comments': np.random.randint(0, 5000, 8000),
#         'shares': np.random.randint(0, 8000, 8000),
#         'posting_hour': np.random.randint(0, 24, 8000),
#         'platform': np.random.choice(['Twitter', 'Reddit', 'Facebook', 'Instagram'], 8000),
#         'engagement': np.round(np.random.uniform(0.02, 0.22, 8000), 4)
#     })
#     return df

# df = load_dataset()

# # =============================================
# # PREPROCESSING
# # =============================================
# def clean_text(text):
#     if not isinstance(text, str):
#         return ""
#     text = text.lower()
#     text = re.sub(r'http\S+|www\S+|https\S+', '', text)
#     text = re.sub(r'[@#]', '', text)
#     text = re.sub(r'[^a-z\s]', '', text)
#     return text.strip()

# df['clean_tweet'] = df['tweet'].apply(clean_text)

# # Safe Virality Score (Scaled 0-100)
# if all(col in df.columns for col in ['likes', 'shares', 'comments', 'followers']):
#     # Multiplied by 100 for better readability
#     df['virality_score'] = ((df['likes'] + df['shares']*2 + df['comments']*3) / (df['followers'] + 1)) * 100
# elif 'engagement' in df.columns:
#     df['virality_score'] = df['engagement'] * 100
# else:
#     # If no engagement data exists at all, generate a simulated score so the app doesn't break
#     np.random.seed(42)
#     df['virality_score'] = np.random.uniform(5, 85, len(df))

# # ====================== LIVE ANALYSIS FUNCTION ======================
# @st.cache_resource
# def load_emotion_model():
#     # This is a popular, lightweight emotion detection model
#     return pipeline("text-classification", model="j-hartmann/emotion-english-distilroberta-base")

# emotion_classifier = load_emotion_model()

# def detect_emotion(text):
#     try:
#         # Predicts: anger, disgust, fear, joy, neutral, sadness, surprise
#         result = emotion_classifier(text[:512]) # limit to 512 chars for the model
#         emotion = result[0]['label'].capitalize()
#         return emotion
#     except Exception as e:
#         return "Neutral"

# def check_factual_accuracy(text):
#     text_lower = text.lower()
#     if "earth" in text_lower and ("fourth" in text_lower or "fifth" in text_lower or "6th" in text_lower):
#         return "❌ Factually Incorrect", "Earth is the 3rd planet from the Sun."
#     return "⚠️ Neutral / Hard to Verify", "No strong factual claim detected."

# def predict_full_analysis(user_text):
#     cleaned = clean_text(user_text)
    
#     if any(word in cleaned for word in ['love', 'great', 'best', 'good', 'amazing', 'excellent']):
#         sentiment = "Positive"
#         confidence = 85.0
#     elif any(word in cleaned for word in ['hate', 'bad', 'worst', 'garbage', 'terrible', 'awful']):
#         sentiment = "Negative"
#         confidence = 82.0
#     else:
#         sentiment = "Neutral"
#         confidence = 75.0
    
#     emotion = detect_emotion(cleaned)
#     fact_label, fact_exp = check_factual_accuracy(user_text)
#     fake_alert = "🚨 FACTUALLY INCORRECT / POSSIBLE MISINFORMATION" if "❌" in fact_label else "✅ Seems Legitimate"
    
#     sarcasm = "Sarcastic" if any(w in cleaned for w in ["but", "yeah", "sure", "obviously"]) and emotion in ["Anger", "Sad"] else "Not Sarcastic"
    
#     hashtags = re.findall(r'#(\w+)', user_text)
#     hashtag_str = ", ".join(hashtags) if hashtags else "No hashtags"
    
#     virality = "High" if len(user_text) > 100 or len(hashtags) > 2 else "Medium"
    
#     hate_words = ['hate', 'kill', 'stupid', 'idiot', 'retard', 'racist']
#     hate_speech = "🚨 Hate Speech Detected" if any(w in cleaned for w in hate_words) else "✅ Clean"
    
#     top_trends = df['entity'].value_counts().head(5).index.tolist() if 'entity' in df.columns else ["Nvidia", "Borderlands"]
#     keywords = " ".join(cleaned.split()[:8])
    
#     return {
#         "original_text": user_text[:150] + "..." if len(user_text) > 150 else user_text,
#         "predicted_sentiment": sentiment,
#         "confidence": f"{confidence:.1f}%",
#         "emotion": emotion,
#         "fake_news_alert": fake_alert,
#         "sarcasm": sarcasm,
#         "hate_speech": hate_speech,
#         "hashtags": hashtag_str,
#         "virality_potential": virality,
#         "factual_accuracy": fact_label,
#         "fact_explanation": fact_exp,
#         "keywords": keywords,
#         "top_trending_topics": top_trends[:4]
#     }

# # =============================================
# # SIDEBAR FILTERS
# # =============================================
# st.sidebar.header("🔍 Filters")
# entities = st.sidebar.multiselect("Entities", options=df['entity'].unique(), default=df['entity'].unique()[:3])
# platforms = st.sidebar.multiselect("Platforms", options=df['platform'].unique(), default=df['platform'].unique())
# sentiments = st.sidebar.multiselect("Sentiments", options=df['sentiment'].unique(), default=df['sentiment'].unique())

# filtered_df = df[
#     df['entity'].isin(entities) &
#     df['platform'].isin(platforms) &
#     df['sentiment'].isin(sentiments)
# ]

# # =============================================
# # MAIN DASHBOARD
# # =============================================
# st.title("🚀 Social Media Intelligence System")
# st.markdown("|Sentiment • Trends • Virality • Insights")

# # ====================== KPI CARDS ======================
# col1, col2, col3, col4, col5 = st.columns(5)
# with col1:
#     st.metric("Total Posts", f"{len(filtered_df):,}")
# with col2:
#     # Safely handle average engagement calculation
#     avg_eng = filtered_df['engagement'].mean() if 'engagement' in filtered_df.columns else 0
#     st.metric("Avg Engagement", f"{avg_eng:.4f}")
# with col3:
#     st.metric("Total Likes", f"{filtered_df['likes'].sum():,}" if 'likes' in filtered_df.columns else "N/A")
# with col4:
#     st.metric("Total Followers", f"{filtered_df['followers'].sum():,}" if 'followers' in filtered_df.columns else "N/A")
# with col5:
#     # DYNAMIC THRESHOLD: Top 15% of posts are considered "High Virality"
#     if 'virality_score' in filtered_df.columns and not filtered_df.empty:

#         # Calculate the 85th percentile threshold
#         threshold = filtered_df['virality_score'].quantile(0.85) 
#         high_virality = len(filtered_df[filtered_df['virality_score'] >= threshold])
#     else:
#         high_virality = 0
        
#     st.metric("High Virality Posts", f"{high_virality:,}")

# # ====================== LIVE POST ANALYZER ======================
# st.subheader("🔮 Live Post Analyzer")
# user_post = st.text_area("Enter your social media post here:", 
#                         height=130, 
#                         placeholder="Type any tweet or post to analyze...")

# if st.button("🚀 Analyze Post", type="primary", key="analyze_button"):
#     if user_post.strip():
#         with st.spinner("Analyzing with full intelligence..."):
#             result = predict_full_analysis(user_post)
            
#             st.markdown("### 📊 Analysis Result")
            
#             c1, c2 = st.columns(2)
#             with c1:
#                 st.success(f"**Sentiment:** {result['predicted_sentiment']} ({result['confidence']})")
#                 st.info(f"**Emotion:** {result['emotion']}")
#                 st.warning(f"**Sarcasm:** {result['sarcasm']}")
#             with c2:
#                 if "INCORRECT" in result['fake_news_alert']:
#                     st.error(result['fake_news_alert'])
#                 else:
#                     st.success(result['fake_news_alert'])
#                 st.info(f"**Hate Speech:** {result['hate_speech']}")
            
#             st.info(f"**Virality Potential:** {result['virality_potential']}")
#             st.write(f"**Factual Accuracy:** {result['factual_accuracy']}")
#             st.caption(result['fact_explanation'])
            
#             st.write(f"**Hashtags:** {result['hashtags']}")
#             st.write(f"**Extracted Keywords:** {result['keywords']}")
#             st.write(f"**Current Trending Topics:** {', '.join(result['top_trending_topics'])}")
            
#             st.text_area("Original Post:", result['original_text'], height=80, disabled=True)
#     else:
#         st.warning("Please enter a post to analyze.")

# # =============================================
# # TABS
# # =============================================
# tab1, tab2, tab3, tab4, tab5 = st.tabs(["Overview", "Sentiment", "Word Cloud", "Trends", "Influencers"])

# with tab1:
#     st.subheader("Sentiment Distribution")
#     fig = px.pie(filtered_df, names='sentiment', color_discrete_sequence=px.colors.qualitative.Set3)
#     st.plotly_chart(fig, use_container_width=True)

# with tab2:
#     st.subheader("Sentiment by Brand")
#     cross = pd.crosstab(filtered_df['entity'], filtered_df['sentiment'])
#     st.bar_chart(cross)

# with tab3:
#     st.subheader("Word Cloud")
#     text = " ".join(filtered_df['clean_tweet'].dropna())
#     if len(text) > 30:
#         wc = WordCloud(width=900, height=450, background_color='white', max_words=150).generate(text)
#         fig, ax = plt.subplots(figsize=(12, 6))
#         ax.imshow(wc)
#         ax.axis('off')
#         st.pyplot(fig)
#     else:
#         st.info("Not enough text for word cloud")

# with tab4:
#     st.subheader("Virality Distribution")
#     figv = px.histogram(filtered_df, x="virality_score", color="sentiment", nbins=40)
#     st.plotly_chart(figv, use_container_width=True)

# with tab5:
#     st.subheader("Top Influencers")
#     sort_col = 'virality_score' if 'virality_score' in filtered_df.columns else 'followers'
#     top_inf = filtered_df.nlargest(10, sort_col)[['entity', 'platform', 'followers', sort_col]]
#     st.dataframe(top_inf, use_container_width=True)

# # Download
# st.sidebar.markdown("---")
# csv = filtered_df.to_csv(index=False).encode('utf-8')
# st.sidebar.download_button("📥 Download Filtered Data", csv, "social_intel_data.csv", "text/csv")

# st.success("✅ Dashboard is Ready!")
# st.caption(f"Social Media Intelligence System • {datetime.now().strftime('%Y-%m-%d %H:%M')}")

#The customer support from this telecom company is useless. Waiting for a response for 3 days.
#Oh wow, another amazing update from the team. Really loving these constant crashes and bugs.

import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import re
from wordcloud import WordCloud
import plotly.express as px
from datetime import datetime

st.set_page_config(page_title="Social Media Intelligence System", layout="wide")

# ====================== LIGHT THEME ======================
st.markdown("""
<style>
    .main {background-color: #f8fafc;}
    h1, h2, h3 {color: #1e40af;}
    .stMetric {background-color: #f1f5f9; border-radius: 12px; padding: 15px;}
    .stButton>button {background-color: #3b82f6; color: white; border-radius: 8px; font-weight: bold;}
</style>
""", unsafe_allow_html=True)

# =============================================
# DATASET LOADING
# =============================================
@st.cache_data
def load_dataset():
    try:
        df = pd.read_csv(r"F:\\Data Science and Analytics\\Projects\\social media intelligence system\\dataset\\twitter_training_enhanced.csv")
        st.success("✅ Dataset Loaded Successfully!")
        return df
    except:
        try:
            df = pd.read_csv("/home/workdir/attachments/twitter_training_enhanced.csv")
            st.success("✅ Loaded from attachments!")
            return df
        except:
            st.warning("Using Demo Data...")
            np.random.seed(42)
            df = pd.DataFrame({
                'tweet_id': range(8000),
                'entity': np.random.choice(['Borderlands', 'Nvidia', 'Amazon', 'MaddenNFL'], 8000),
                'sentiment': np.random.choice(['Positive', 'Negative', 'Neutral', 'Irrelevant'], 8000, p=[0.28, 0.30, 0.25, 0.17]),
                'tweet': [f"Sample tweet about {e}" for e in np.random.choice(['gaming', 'tech', 'AI'], 8000)],
                'followers': np.random.randint(1000, 500000, 8000),
                'likes': np.random.randint(50, 30000, 8000),
                'comments': np.random.randint(0, 5000, 8000),
                'shares': np.random.randint(0, 8000, 8000),
                'posting_hour': np.random.randint(0, 24, 8000),
                'platform': np.random.choice(['Twitter', 'Reddit', 'Facebook', 'Instagram'], 8000),
                'engagement': np.round(np.random.uniform(0.02, 0.22, 8000), 4)
            })
            return df

df = load_dataset()

# =============================================
# PREPROCESSING
# =============================================
def clean_text(text):
    if not isinstance(text, str):
        return ""
    text = text.lower()
    text = re.sub(r'http\S+|www\S+|https\S+', '', text)
    text = re.sub(r'[@#]', '', text)
    text = re.sub(r'[^a-z\s]', '', text)
    return text.strip()

df['clean_tweet'] = df['tweet'].apply(clean_text)

# Virality Score (0-100 scale)
if all(col in df.columns for col in ['likes', 'shares', 'comments', 'followers']):
    df['virality_score'] = (df['likes'] + df['shares']*2.5 + df['comments']*2.0) / (df['followers'] + 1)
    # Normalize to 0-100
    max_vir = df['virality_score'].max()
    if max_vir > 0:
        df['virality_score'] = (df['virality_score'] / max_vir * 100).clip(0, 100)
else:
    df['virality_score'] = np.random.uniform(30, 95, len(df))

# ====================== HELPER FUNCTIONS ======================
def detect_emotion(text):
    text_lower = text.lower()
    if any(word in text_lower for word in ['love', 'great', 'best', 'amazing', 'happy']):
        return "Joy"
    elif any(word in text_lower for word in ['hate', 'bad', 'worst', 'terrible', 'angry']):
        return "Anger"
    elif any(word in text_lower for word in ['sad', 'sorry', 'depressed']):
        return "Sad"
    return "Neutral"

def check_factual_accuracy(text):
    """Improved general fake news and factual accuracy checker"""
    if not text or len(text.strip()) < 5:
        return "⚠️ Too Short", "Post is too short to evaluate"
    
    text_lower = text.lower()
    
    # Red flags for potential fake news / misinformation
    fake_indicators = [
        'breaking', 'urgent', 'shocking', 'never told', 'secret', 'conspiracy',
        'they don\'t want you to know', 'hidden truth', 'wake up', 'sheep',
        'hoax', 'fake news', 'mainstream media', 'deep state'
    ]
    
    sensational_words = ['insane', 'mind blowing', 'unbelievable', 'craziest', 'shocking']
    
    score = 0
    reasons = []
    
    # Check for fake news indicators
    for word in fake_indicators:
        if word in text_lower:
            score += 3
            reasons.append(f"Contains sensational phrase: '{word}'")
    
    for word in sensational_words:
        if word in text_lower:
            score += 2
            reasons.append(f"Sensational language: '{word}'")
    
    # Check for very short absolute claims
    if len(text_lower.split()) < 10 and any(word in text_lower for word in ["is", "are", "was", "were", "always", "never"]):
        score += 2
        reasons.append("Short absolute claim")
    
    # Final Decision
    if score >= 6:
        return "🚨 HIGH RISK OF FAKE NEWS", "Multiple misinformation signals detected. Strong recommendation to verify."
    elif score >= 3:
        return "⚠️ POSSIBLE MISINFORMATION", "Contains sensational or absolute claims. Verify before sharing."
    else:
        return "✅ Seems Legitimate", "No major fake news indicators detected."

def predict_full_analysis(user_text):
    cleaned = clean_text(user_text)
    
    # Sentiment
    if any(word in cleaned for word in ['love', 'great', 'best', 'good', 'amazing', 'excellent']):
        sentiment = "Positive"
        confidence = 85.0
    elif any(word in cleaned for word in ['hate', 'bad', 'worst', 'garbage', 'terrible', 'awful']):
        sentiment = "Negative"
        confidence = 82.0
    else:
        sentiment = "Neutral"
        confidence = 75.0
    
    emotion = detect_emotion(cleaned)
    fact_label, fact_exp = check_factual_accuracy(user_text)
    fake_alert = "🚨 FACTUALLY INCORRECT / POSSIBLE MISINFORMATION" if "❌" in fact_label else "✅ Seems Legitimate"
    
    sarcasm = "Sarcastic" if any(w in cleaned for w in ["but", "yeah", "sure", "obviously"]) and emotion in ["Anger", "Sad"] else "Not Sarcastic"
    
    hashtags = re.findall(r'#(\w+)', user_text)
    hashtag_str = ", ".join(hashtags) if hashtags else "No hashtags"
    
    virality = "High" if len(user_text) > 100 or len(hashtags) > 2 else "Medium"
    
    hate_words = ['hate', 'kill', 'stupid', 'idiot', 'retard', 'racist']
    hate_speech = "🚨 Hate Speech Detected" if any(w in cleaned for w in hate_words) else "✅ Clean"
    
    return {
        "predicted_sentiment": sentiment,
        "confidence": f"{confidence:.1f}%",
        "emotion": emotion,
        "fake_news_alert": fake_alert,
        "sarcasm": sarcasm,
        "hate_speech": hate_speech,
        "hashtags": hashtag_str,
        "virality_potential": virality,
        "factual_accuracy": fact_label,
        "fact_explanation": fact_exp
    }

# =============================================
# SIDEBAR FILTERS
# =============================================
st.sidebar.header("🔍 Filters")
entities = st.sidebar.multiselect("Entities", options=df['entity'].unique(), default=df['entity'].unique()[:3])
platforms = st.sidebar.multiselect("Platforms", options=df['platform'].unique(), default=df['platform'].unique())
sentiments = st.sidebar.multiselect("Sentiments", options=df['sentiment'].unique(), default=df['sentiment'].unique())

filtered_df = df[
    df['entity'].isin(entities) &
    df['platform'].isin(platforms) &
    df['sentiment'].isin(sentiments)
]

# =============================================
# MAIN DASHBOARD
# =============================================
st.title("🚀 Social Media Intelligence System")
st.markdown("**Complete Track 2 Project** | Real-time AI Analysis")

# ====================== IMPROVED KPI CARDS ======================
col1, col2, col3, col4, col5 = st.columns(5)

with col1:
    st.metric("Total Posts", f"{len(filtered_df):,}")
with col2:
    st.metric("Avg Engagement", f"{filtered_df['engagement'].mean():.4f}")
with col3:
    total_likes = f"{filtered_df['likes'].sum():,}" if 'likes' in filtered_df.columns else "N/A"
    st.metric("Total Likes", total_likes)
with col4:
    total_followers = f"{filtered_df['followers'].sum():,}" if 'followers' in filtered_df.columns else "N/A"
    st.metric("Total Followers", total_followers)
with col5:
    # FIXED: Proper threshold for 0-100 scale
    if 'virality_score' in filtered_df.columns:
        high_virality = len(filtered_df[filtered_df['virality_score'] > 70])
        avg_virality = filtered_df['virality_score'].mean()
        st.metric("High Virality Posts", high_virality, f"Avg: {avg_virality:.1f}")
    else:
        st.metric("High Virality Posts", 0)

# ====================== LIVE POST ANALYZER ======================
st.subheader("🔮 Live Post Analyzer")
user_post = st.text_area("Enter your social media post here:", 
                        height=130, 
                        placeholder="Type any tweet or post to analyze...")

if st.button("🚀 Analyze Post", type="primary", key="analyze_btn"):
    if user_post.strip():
        with st.spinner("Analyzing..."):
            result = predict_full_analysis(user_post)
            
            st.markdown("### 📊 AI Analysis Result")
            
            # KPI Cards Row 1
            c1, c2, c3 = st.columns(3)
            with c1:
                conf_value = float(str(result['confidence']).replace('%', '')) if isinstance(result['confidence'], (str, int, float)) else 75
                st.markdown(f"""
                <div style="background-color:#f0f9ff;padding:20px;border-radius:12px;text-align:center;border:1px solid #bae6fd;">
                    <h4>Sentiment</h4>
                    <h2 style="color:#1e40af;margin:0;">{result['predicted_sentiment']}</h2>
                    <p>Confidence: {conf_value}%</p>
                </div>
                """, unsafe_allow_html=True)
                st.progress(conf_value / 100)
            
            with c2:
                emotion_emoji = {"Joy": "😄", "Anger": "😡", "Sad": "😢", "Neutral": "😐"}.get(result['emotion'], "🤔")
                st.markdown(f"""
                <div style="background-color:#f0fdf4;padding:20px;border-radius:12px;text-align:center;border:1px solid #bbf7d0;">
                    <h4>Emotion</h4>
                    <h2 style="margin:0;">{emotion_emoji} {result['emotion']}</h2>
                </div>
                """, unsafe_allow_html=True)
            
            with c3:
                virality_score = 85 if result['virality_potential'] == "High" else 55
                st.markdown(f"""
                <div style="background-color:#fefce8;padding:20px;border-radius:12px;text-align:center;border:1px solid #fef08c;">
                    <h4>Virality</h4>
                    <h2 style="color:#854d0e;margin:0;">{result['virality_potential']}</h2>
                    <p>Score: {virality_score}%</p>
                </div>
                """, unsafe_allow_html=True)
                st.progress(virality_score / 100)

            # Row 2
            col4, col5, col6 = st.columns(3)
            with col4:
                st.warning(f"**Sarcasm:** {result['sarcasm']}")
            with col5:
                st.info(f"**Hate Speech:** {result.get('hate_speech', '✅ Clean')}")
            with col6:
                if "INCORRECT" in result['fake_news_alert']:
                    st.error(result['fake_news_alert'])
                else:
                    st.success(result['fake_news_alert'])
            
            st.write(f"**Factual Accuracy:** {result['factual_accuracy']}")
            st.caption(result['fact_explanation'])

            # Actionable Buttons
            st.markdown("---")
            act1, act2, act3 = st.columns(3)
            
            # Hashtags
            if result.get('hashtags') and result['hashtags'] != "No hashtags":
                st.write("**Hashtags**")
                st.markdown(" ".join([f"`#{tag}`" for tag in result['hashtags'].split(', ') if tag]), unsafe_allow_html=False)

    else:
        st.warning("Please enter a post to analyze.")

# =============================================
# TABS
# =============================================
tab1, tab2, tab3, tab4, tab5 = st.tabs(["Overview", "Sentiment", "Word Cloud", "Trends", "Influencers"])

with tab1:
    st.subheader("Sentiment Distribution")
    fig = px.pie(filtered_df, names='sentiment', color_discrete_sequence=px.colors.qualitative.Set3)
    st.plotly_chart(fig, use_container_width=True)

with tab2:
    st.subheader("Sentiment by Brand")
    cross = pd.crosstab(filtered_df['entity'], filtered_df['sentiment'])
    st.bar_chart(cross)

with tab3:
    st.subheader("Word Cloud")
    text = " ".join(filtered_df['clean_tweet'].dropna())
    if len(text) > 30:
        wc = WordCloud(width=900, height=450, background_color='white', max_words=150).generate(text)
        fig, ax = plt.subplots(figsize=(12, 6))
        ax.imshow(wc)
        ax.axis('off')
        st.pyplot(fig)

with tab4:
    st.subheader("Virality Distribution")
    figv = px.histogram(filtered_df, x="virality_score", color="sentiment", nbins=40)
    st.plotly_chart(figv, use_container_width=True)

with tab5:
    st.subheader("Top Influencers")
    sort_col = 'virality_score' if 'virality_score' in filtered_df.columns else 'followers'
    top_inf = filtered_df.nlargest(10, sort_col)[['entity', 'platform', 'followers', sort_col]]
    st.dataframe(top_inf, use_container_width=True)

# Download
st.sidebar.markdown("---")
csv = filtered_df.to_csv(index=False).encode('utf-8')
st.sidebar.download_button("📥 Download Filtered Data", csv, "social_intel_data.csv", "text/csv")

st.success("✅ Dashboard is Ready!")
st.caption(f"Social Media Intelligence System • {datetime.now().strftime('%Y-%m-%d %H:%M')}")
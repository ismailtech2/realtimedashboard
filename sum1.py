import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import time
import random
from collections import deque

# Set page configuration
st.set_page_config(
    layout="wide",
    page_title="Israel-Palestine Social Pulse",
    initial_sidebar_state="collapsed"
)

# Custom CSS for a more modern look
st.markdown("""
    <style>
        .main {
            padding: 0rem 0.5rem !important;
            background-color: #1a1a1a;
            color: white;
        }
        .block-container {
            padding: 0.5rem;
            max-width: 100%;
        }
        .element-container {
            margin-bottom: 0.5rem;
        }
        .stMetric {
            background-color: #2d2d2d;
            padding: 1rem;
            border-radius: 10px;
            border: 1px solid #3d3d3d;
        }
        .stMetric label {
            color: #00aaff !important;
        }
        [data-testid="stMetricValue"] {
            color: white !important;
        }
        #MainMenu {visibility: hidden;}
        header {visibility: hidden;}
        footer {visibility: hidden;}
    </style>
""", unsafe_allow_html=True)

# Initialize session state
if 'data_queue' not in st.session_state:
    st.session_state.data_queue = deque(maxlen=300)  # Store 5 minutes of data
    st.session_state.last_update = datetime.now()
    st.session_state.total_interactions = 0
    st.session_state.peak_engagement = 0
    st.session_state.average_sentiment = 0

def generate_realistic_tweet():
    """Generate more realistic tweet data with patterns specific to Israel-Palestine conflict"""
    now = datetime.now()
    hour = now.hour
    
    # Topics relevant to the Israel-Palestine conflict
    topics = {
        'Conflict Updates': ['Violence in Gaza', 'Clashes in Jerusalem', 'Military operation updates', 'Rocket fire reported'],
        'Peace Talks': ['New peace talk initiatives', 'International support for ceasefire', 'Diplomatic solutions', 'Global efforts to resolve conflict'],
        'Human Rights': ['Civilian casualties', 'Human rights violations', 'Reports of forced evictions', 'International calls for human rights protection'],
        'International Reactions': ['Global protests', 'UN Security Council debate', 'Global condemnation', 'International support for one side'],
    }

    # Time-based weights for different topics
    if 8 <= hour <= 16:  # During day time
        topic_weights = [0.3, 0.3, 0.2, 0.2]
    elif 16 <= hour <= 22:  # Evening
        topic_weights = [0.3, 0.4, 0.1, 0.2]
    else:  # Late night
        topic_weights = [0.4, 0.3, 0.1, 0.2]
    
    # Select topic and content
    topic = random.choices(list(topics.keys()), weights=topic_weights)[0]
    content = random.choice(topics[topic])
    
    # Generate engagement metrics based on topic and time
    base_engagement = random.gauss(50, 20)
    engagement_multiplier = 1.5 if 9 <= hour <= 20 else 0.7
    
    # Add some randomized trending topics
    trending = random.random() < 0.1  # 10% chance of being a trending topic
    if trending:
        base_engagement *= 2.5
    
    # Generate sentiment with a more conflict-driven distribution
    sentiment_base = random.gauss(0.2, 0.6)  # Slightly more polarized sentiment
    sentiment = max(min(sentiment_base, 1), -1)
    
    # Emotion selection based on sentiment and the sensitive nature of the topic
    if sentiment > 0.3:
        emotion = random.choice(['hope', 'peace', 'joy'])
    elif sentiment < -0.3:
        emotion = random.choice(['anger', 'fear', 'sadness'])
    else:
        emotion = random.choice(['neutral', 'concern', 'sympathy'])
        
    return {
        'id': ''.join(random.choices('0123456789', k=10)),
        'created_at': now,
        'text': f"{content} #{topic.replace(' ', '')}",
        'topic': topic,
        'sentiment_polarity': sentiment,
        'emotion': emotion,
        'retweet_count': int(max(base_engagement * engagement_multiplier * random.uniform(0.8, 1.2), 0)),
        'reply_count': int(max(base_engagement * engagement_multiplier * random.uniform(0.3, 0.6), 0)),
        'like_count': int(max(base_engagement * engagement_multiplier * random.uniform(1.2, 1.8), 0)),
        'is_trending': trending,
        'user_followers': int(random.gauss(1000, 500)),
        'user_verified': random.random() < 0.2,
        'latitude': random.uniform(25, 50),
        'longitude': random.uniform(-130, -60),
        'engagement_score': int(max(base_engagement * engagement_multiplier, 0))
    }

def update_dashboard():
    # Generate new data
    new_tweet = generate_realistic_tweet()

    # Ensure each dictionary has the same structure by checking keys
    if len(st.session_state.data_queue) == 0:
        # Initialize the queue with column names if it's the first entry
        st.session_state.data_queue.append(new_tweet)
    else:
        # Append only if the structure matches the first tweet
        expected_keys = list(st.session_state.data_queue[0].keys())
        if set(new_tweet.keys()) == set(expected_keys):
            st.session_state.data_queue.append(new_tweet)
        else:
            raise ValueError("Mismatch in data structure.")

    # Convert queue to DataFrame
    df = pd.DataFrame(list(st.session_state.data_queue))
    
    # Update metrics
    st.session_state.total_interactions += (
        new_tweet['retweet_count'] + 
        new_tweet['reply_count'] + 
        new_tweet['like_count']
    )
    st.session_state.peak_engagement = max(
        st.session_state.peak_engagement,
        new_tweet['engagement_score']
    )
    st.session_state.average_sentiment = df['sentiment_polarity'].mean()
    
    return df

def create_dashboard():
    # Title with animation
    st.markdown("""
        <h1 style='text-align: center; color: #00aaff; margin: 0; padding: 0;'>
            🕊️ Israel-Palestine Conflict Social Pulse
        </h1>
        <p style='text-align: center; color: #888; margin: 0; padding: 0;'>
            Real-time Social Media Analytics on Israel-Palestine Conflict
        </p>
    """, unsafe_allow_html=True)
    
    # Update data
    df = update_dashboard()
    
    # Filters for topic, emotion, and sentiment
    topic_filter = st.sidebar.selectbox("Filter by Topic", ['All', 'Conflict Updates', 'Peace Talks', 'Human Rights', 'International Reactions'])
    emotion_filter = st.sidebar.selectbox("Filter by Emotion", ['All', 'anger', 'fear', 'sadness', 'hope', 'neutral'])
    sentiment_filter = st.sidebar.selectbox("Filter by Sentiment", ['All', 'Positive', 'Negative', 'Neutral'])
    
    # Filter data based on selected filters
    if topic_filter != 'All':
        df = df[df['topic'] == topic_filter]
    if emotion_filter != 'All':
        df = df[df['emotion'] == emotion_filter]
    if sentiment_filter != 'All':
        if sentiment_filter == 'Positive':
            df = df[df['sentiment_polarity'] > 0.3]
        elif sentiment_filter == 'Negative':
            df = df[df['sentiment_polarity'] < -0.3]
        elif sentiment_filter == 'Neutral':
            df = df[(df['sentiment_polarity'] >= -0.3) & (df['sentiment_polarity'] <= 0.3)]
    
    # Key metrics with dynamic coloring
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        sentiment = df['sentiment_polarity'].mean()
        color = 'green' if sentiment > 0 else 'red'
        st.metric(
            "Sentiment Pulse",
            f"{sentiment:.2f}",
            delta=f"{(sentiment - df['sentiment_polarity'].iloc[-2] if len(df) > 1 else 0):.3f}"
        )
    
    with col2:
        engagement_rate = (df['engagement_score'].mean() / 100)
        st.metric(
            "Engagement Rate",
            f"{engagement_rate:.1f}%",
            delta=f"{(engagement_rate - df['engagement_score'].iloc[-2]/100 if len(df) > 1 else 0):.1f}%"
        )
    
    with col3:
        trend_count = df['is_trending'].sum()
        st.metric(
            "Trending Topics",
            int(trend_count),
            delta=f"{int(trend_count - (0 if len(df) <= 1 else df['is_trending'].iloc[:-1].sum()))}"
        )
    
    with col4:
        st.metric(
            "Peak Engagement",
            st.session_state.peak_engagement,
            delta=f"Total: {st.session_state.total_interactions}"
        )
    
    with col5:
        st.metric("Average Sentiment", f"{st.session_state.average_sentiment:.2f}")
    
    # Main visualizations
    col1, col2 = st.columns(2)
    
    with col1:
        # Real-time sentiment and engagement
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=df['created_at'],
            y=df['sentiment_polarity'],
            name='Sentiment',
            line=dict(color='#00aaff', width=2)
        ))
        fig.add_trace(go.Scatter(
            x=df['created_at'],
            y=df['engagement_score'] / 100,
            name='Engagement',
            line=dict(color='#ff00aa', width=2),
            yaxis='y2'
        ))
        
        fig.update_layout(
            title='Real-time Sentiment & Engagement on the Israel-Palestine Conflict',
            height=300,
            width=800,
            margin=dict(l=20, r=20, t=40, b=20),
            paper_bgcolor='#2d2d2d',
            plot_bgcolor='#2d2d2d',
            font=dict(color='white'),
            yaxis=dict(title='Sentiment', showgrid=False),
            yaxis2=dict(title='Engagement', overlaying='y', side='right', showgrid=False),
            legend=dict(
                yanchor="top",
                y=0.99,
                xanchor="left",
                x=0.01,
                bgcolor='rgba(0,0,0,0)'
            )
        )
        st.plotly_chart(fig, use_container_width=True)  
    
    with col2:
        # Latest Trending Topics with sentiment
        df['sentiment_category'] = df['sentiment_polarity'].apply(
            lambda x: 'Positive' if x > 0.3 else ('Negative' if x < -0.3 else 'Neutral')
        )
        trending_df = df[df['is_trending']].tail(5)
        fig = go.Figure(go.Table(
            header=dict(
                values=['Time', 'Trending Topic', 'Sentiment'],
                fill_color='#00aaff',
                align='left',
                font=dict(color='white')
            ),
            cells=dict(
                values=[
                    trending_df['created_at'].dt.strftime('%H:%M:%S'),
                    trending_df['text'],
                    trending_df['sentiment_category']
                ],
                fill_color='#2d2d2d',
                align='left',
                font=dict(color='white')
            )
        ))
        fig.update_layout(
            title='Live Trending Topics in Israel-Palestine Conflict',
            height=300,
            margin=dict(l=20, r=20, t=40, b=20),
            paper_bgcolor='#2d2d2d'
        )
        st.plotly_chart(fig, use_container_width=True)
    
    # Bottom row
    col1, col2, col3 = st.columns(3)
    
    with col1:
        # Emotion Distribution
        emotion_counts = df['emotion'].value_counts()
        fig = px.pie(
            values=emotion_counts.values,
            names=emotion_counts.index,
            title='Emotional Pulse on the Israel-Palestine Conflict'
        )
        fig.update_layout(
            height=300,
            margin=dict(l=20, r=20, t=40, b=20),
            paper_bgcolor='#2d2d2d',
            plot_bgcolor='#2d2d2d',
            font=dict(color='white')
        )
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # Topic Distribution with Engagement
        topic_engagement = df.groupby('topic')['engagement_score'].mean().sort_values(ascending=True)
        fig = go.Figure()
        fig.add_trace(go.Bar(
            y=topic_engagement.index,
            x=topic_engagement.values,
            orientation='h',
            marker=dict(
                color=topic_engagement.values,
                colorscale='Viridis'
            )
        ))
        
        fig.update_layout(
            title='Topic Engagement Analysis in the Israel-Palestine Conflict',
            height=300,
            margin=dict(l=20, r=20, t=40, b=20),
            paper_bgcolor='#2d2d2d',
            plot_bgcolor='#2d2d2d',
            font=dict(color='white'),
            xaxis=dict(title='Average Engagement', showgrid=False),
            yaxis=dict(title='Topic', showgrid=False)
        )
        st.plotly_chart(fig, use_container_width=True)
    
    with col3:
        # Interactive Map with sentiment and engagement
        df['sentiment_category'] = df['sentiment_polarity'].apply(
            lambda x: 'Positive' if x > 0.3 else ('Negative' if x < -0.3 else 'Neutral')
        )
        
        fig = px.scatter_mapbox(
            df,
            lat='latitude',
            lon='longitude',
            color='sentiment_category',
            size='engagement_score',
            hover_data=['text', 'sentiment_polarity'],
            title='Geographic Sentiment and Engagement on Israel-Palestine Conflict',
            mapbox_style='carto-darkmatter'
        )
        
        fig.update_layout(
            height=300,
            width=400,
            margin=dict(l=20, r=20, t=40, b=20),
            paper_bgcolor='#2d2d2d',
            font=dict(color='white'),
            mapbox=dict(
                center=dict(lat=31.7683, lon=35.2137),  # Center over Israel-Palestine region
                zoom=6  # Adjust zoom level to focus on Israel and Palestine
            )
        )
        
        st.plotly_chart(fig, use_container_width=True)

if __name__ == "__main__":
    while True:
        create_dashboard()
        time.sleep(1)  # Update every second
        st.rerun()  # Replaces experimental_rerun() with rerun()

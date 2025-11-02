import streamlit as st
import requests
import json
import os
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import re
import fitz  # PyMuPDF for PDF summarization
from textblob import TextBlob
from PIL import Image

# ---------- MedPal Branding Images ----------
BANNER_PATH = "assets/banner.png"
LOGO_PATH = "assets/logo.png"
PAL_PATH = "assets/pal.png"

# ----------------------------
# CONFIG
# ----------------------------
st.set_page_config(page_title="MedPal", page_icon="🩺", layout="wide")
API_URL = "http://127.0.0.1:5000/query"
LOG_PATH = "data/mood_logs.json"
MEM_PATH = "backend/memory.json"
DECK_PATH = "data/study_deck.json"

# ----------------------------
# SIDEBAR – MEMORY SNAPSHOT
# ----------------------------
st.sidebar.header("🧠 MedPal Memory Snapshot")
if os.path.exists(MEM_PATH):
    try:
        memory = json.load(open(MEM_PATH))
        sessions = memory.get("sessions", [])[-7:]
        if sessions:
            for s in reversed(sessions):
                border_color = "#2E7D32" if s["mode"] == "wellness" else "#B71C1C"
                st.sidebar.markdown(
                    f"<div style='border:2px solid {border_color};padding:8px;border-radius:8px;margin-bottom:6px;'>"
                    f"<b>{s['mode'].capitalize()}</b> • {s['timestamp']}<br>"
                    f"<i>{s['query']}</i><br>"
                    f"<small>{s['reply'][:90]}...</small></div>",
                    unsafe_allow_html=True
                )
        else:
            st.sidebar.info("No prior sessions yet.")
    except Exception as e:
        st.sidebar.warning(f"Error reading memory: {e}")
else:
    st.sidebar.info("No memory file found.")

if st.sidebar.button("🗑️ Clear Memory"):
    if os.path.exists(MEM_PATH):
        json.dump({"sessions": []}, open(MEM_PATH, "w"))
        st.sidebar.success("Memory cleared! Refresh the app.")

st.sidebar.markdown("---")
st.sidebar.caption("© MedPal | Built with ❤️ by Anisha & Rohan")

# ----------------------------
# MAIN LAYOUT
# ----------------------------
# ----------------------------
# Header Images
# ----------------------------
# Show top banner (non-intrusive, keeps your colors)
if os.path.exists(BANNER_PATH):
    st.image(BANNER_PATH, use_container_width=True)

# Sidebar logo
with st.sidebar:
    if os.path.exists(LOGO_PATH):
        st.image(LOGO_PATH, width=120)

tab1, tab2, tab3 = st.tabs(["💬 Chat with MedPal", "📊 Wellness Insights", "🎓 Study Deck"])

# ----------------------------
# TAB 1 – CHAT INTERFACE
# ----------------------------
with tab1:
    # st.title("🩺 MedPal – Your Academic + Wellness Companion")
    # st.markdown("_Because studying smarter only works when you're feeling better._")
    # ----------------------------
    # Hero Header with Mascot
    # ----------------------------
    col1, col2 = st.columns([1, 4])
    with col1:
        if os.path.exists(PAL_PATH):
            st.image(PAL_PATH, width=130)
    with col2:
        st.markdown(
            """
            <h1 style='font-size: 42px; color: white;'>
            🩺 MedPal – Your Academic + Wellness Companion
            </h1>
            <p style='font-size:18px; color: #bbbbbb;'>
            Because studying smarter only works when you're feeling better.
            </p>
            """,
            unsafe_allow_html=True
        )

    col1, col2 = st.columns([4, 1])
    with col2:
        mode = st.radio("Mode", ["auto", "academic", "wellness"], horizontal=False)
    with col1:
        query = st.text_input("💬 Type your question or feeling here:")

    # 📄 Optional PDF upload (used only in academic mode)
    uploaded_pdf = st.file_uploader("📄 Upload a PDF to summarize or use in your query (optional)", type=["pdf"])

    if st.button("Ask MedPal"):
        if not query.strip() and uploaded_pdf is None:
            st.warning("Please enter a message or upload a PDF first.")
        else:
            try:
                # --- Extract text if PDF uploaded ---
                pdf_text = ""
                if uploaded_pdf is not None:
                    try:
                        pdf = fitz.open(stream=uploaded_pdf.read(), filetype="pdf")
                        for page in pdf:
                            pdf_text += page.get_text("text")
                        st.info("✅ PDF loaded successfully!")
                    except Exception as e:
                        st.error(f"PDF reading failed: {e}")

                # --- Combine user query and PDF text ---
                final_query = query
                if pdf_text.strip():
                    final_query += f"\n\nPlease summarize or create study notes from this document:\n{pdf_text[:8000]}"

                # --- Send request ---
                res = requests.post(API_URL, json={"query": final_query, "mode": mode})
                if res.status_code == 200:
                    data = res.json()
                    reply = data.get("reply", "")
                    mode_used = data["mode"]

                    # User message
                    st.markdown(
                        f"<div style='border:2px solid #757575;padding:10px;border-radius:10px;margin:8px 0;'>"
                        f"<b>You:</b> {query}</div>",
                        unsafe_allow_html=True
                    )

                    border_color = "#2E7D32" if mode_used == "wellness" else "#B71C1C"

                    # --- Detect flashcards ---
                    def extract_flashcards(text):
                        clean_text = re.sub(r'\*\*|__|###|==|--|_', '', text)
                        pattern = r"(?:Card\s*\d+|Flashcard\s*\d+|Q\d+|^\d+\.|Brain.*Card\s*\d+)?\s*Front:\s*(.*?)\s*(?:Back:|Answer:)\s*(.*?)(?=\n(?:Card|Flashcard|Q\d+|\d+\.|Front:|Answer:|$))"
                        cards = re.findall(pattern, clean_text, re.DOTALL | re.MULTILINE)
                        return [(f.strip(), b.strip()) for f, b in cards if f.strip() and b.strip()]

                    flashcards = extract_flashcards(reply)

                    # --- If flashcards exist ---
                    if flashcards:
                        st.markdown(
                            f"<div style='border:2px solid {border_color};padding:10px;border-radius:10px;margin:8px 0;'>"
                            f"<b>MedPal ({mode_used.title()} Mode):</b> Here are your flashcards ⤵️</div>",
                            unsafe_allow_html=True
                        )

                        # CSS for flip-cards
                        st.markdown("""
                        <style>
                        .deck {
                            display: flex;
                            flex-wrap: wrap;
                            justify-content: center;
                            align-items: flex-start;
                            gap: 30px;
                            margin-top: 25px;
                            margin-bottom: 25px;
                            width: 100%;
                            max-width: 1200px;
                            margin-left: auto;
                            margin-right: auto;
                        }
                        .flip-card {
                            background-color: transparent;
                            flex: 1 1 300px;
                            max-width: 320px;
                            min-width: 260px;
                            perspective: 1000px;
                            cursor: pointer;
                            display: flex;
                            justify-content: center;
                        }
                        .flip-card-inner {
                            position: relative;
                            width: 100%;
                            min-height: 230px;
                            text-align: center;
                            transition: transform 0.8s ease-in-out;
                            transform-style: preserve-3d;
                        }
                        .flip-card:hover .flip-card-inner { transform: rotateY(180deg); }
                        .flip-card-front, .flip-card-back {
                            position: absolute;
                            width: 100%;
                            min-height: 230px;
                            box-sizing: border-box;
                            backface-visibility: hidden;
                            border-radius: 14px;
                            padding: 20px 18px;
                            display: flex;
                            flex-direction: column;
                            align-items: center;
                            justify-content: center;
                            font-size: 15.5px;
                            line-height: 1.5;
                            word-wrap: break-word;
                            overflow-wrap: break-word;
                            text-align: center;
                            color: white;
                        }
                        .flip-card-front {
                            background-color: #1E1E1E;
                            border: 2px solid #B71C1C;
                            box-shadow: 0 0 10px rgba(183, 28, 28, 0.4);
                        }
                        .flip-card-back {
                            background-color: #1E1E1E;
                            border: 2px solid #2E7D32;
                            box-shadow: 0 0 10px rgba(46, 125, 50, 0.4);
                            transform: rotateY(180deg);
                            color: #C8E6C9;
                        }
                        .q-label {
                            font-size: 17px;
                            font-weight: 700;
                            color: #FFB300;
                            margin-bottom: 10px;
                        }
                        @media (max-width: 1100px) { .flip-card { flex: 1 1 45%; } }
                        @media (max-width: 700px) { .flip-card { flex: 1 1 90%; } }
                        </style>
                        """, unsafe_allow_html=True)

                        st.markdown("<div class='deck'>", unsafe_allow_html=True)
                        for i, (front, back) in enumerate(flashcards, 1):
                            card_html = f"""
                            <div class="flip-card">
                                <div class="flip-card-inner">
                                    <div class="flip-card-front">
                                        <div class="q-label">🧠 Q{i}</div>
                                        {front}
                                    </div>
                                    <div class="flip-card-back">
                                        <div class="q-label">✅ Answer</div>
                                        {back}
                                    </div>
                                </div>
                            </div>
                            """
                            st.markdown(card_html, unsafe_allow_html=True)
                        st.markdown("</div>", unsafe_allow_html=True)

                        # Save flashcards
                        os.makedirs("data", exist_ok=True)
                        deck = json.load(open(DECK_PATH)) if os.path.exists(DECK_PATH) else []
                        topic = query.strip().capitalize()
                        for f, b in flashcards:
                            deck.append({"topic": topic, "front": f, "back": b, "mastered": False})
                        json.dump(deck, open(DECK_PATH, "w"), indent=2)
                        st.success(f"✅ {len(flashcards)} flashcards saved to Study Deck!")

                    else:
                        # --- Normal response (fixed Markdown rendering) ---
                        st.markdown(f"""
                        <div style='border:2px solid {border_color};padding:10px;border-radius:10px;margin:8px 0;'>
                        <b>MedPal ({mode_used.title()} Mode):</b>
                        </div>
                        """, unsafe_allow_html=True)
                        st.markdown(reply)

                    # --- LOGGING ---
                    os.makedirs("data", exist_ok=True)
                    logs = json.load(open(LOG_PATH)) if os.path.exists(LOG_PATH) else []
                    logs.append({
                        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        "mode": mode_used,
                        "query": query,
                        "reply": reply
                    })
                    json.dump(logs, open(LOG_PATH, "w"), indent=2)

                else:
                    st.error(f"Server error: {res.status_code}")
            except Exception as e:
                st.error(f"Connection failed: {e}")

# ----------------------------
# TAB 2 – WELLNESS INSIGHTS
# ----------------------------
from textblob import TextBlob

with tab2:
    st.title("📊 Wellness Insights & Activity Trends")

    # --- Date Filter ---
    st.subheader("📅 Select Time Period")
    time_filter = st.selectbox("Choose time window", ["All Time", "Last 7 Days", "Last 30 Days"])
    
    if os.path.exists(LOG_PATH):
        try:
            df = pd.read_json(LOG_PATH)
            if not df.empty:
                df["timestamp"] = pd.to_datetime(df["timestamp"])
                df = df.sort_values("timestamp")

                # --- Filter by time window ---
                if time_filter == "Last 7 Days":
                    df = df[df["timestamp"] >= (datetime.now() - pd.Timedelta(days=7))]
                elif time_filter == "Last 30 Days":
                    df = df[df["timestamp"] >= (datetime.now() - pd.Timedelta(days=30))]

                if df.empty:
                    st.warning("No data found for the selected period.")
                else:
                    # --- PIE: Mode Frequency ---
                    st.subheader("🎯 Mode Distribution")
                    pie = px.pie(df, names="mode", title="Academic vs Wellness Activity",
                                 color_discrete_sequence=["#F28B82", "#A5D6A7"])
                    pie.update_traces(textposition="inside", textinfo="percent+label")
                    st.plotly_chart(pie, use_container_width=True)

                    # --- TIMELINE ---
                    st.subheader("🧭 Mode Timeline")
                    df["numeric_time"] = range(len(df))
                    colors = {"academic": "#E57373", "wellness": "#81C784"}
                    line = go.Figure()
                    for m in df["mode"].unique():
                        subset = df[df["mode"] == m]
                        line.add_trace(go.Scatter(
                            x=subset["timestamp"], y=subset["numeric_time"],
                            mode="markers+lines", name=m.title(),
                            marker=dict(size=9, color=colors[m]),
                            line=dict(width=2)
                        ))
                    line.update_layout(title="Session Mode Over Time",
                                       yaxis_title="Session Count",
                                       xaxis_title="Timestamp")
                    st.plotly_chart(line, use_container_width=True)

                    # --- GAUGE: Productivity Ratio ---
                    st.subheader("📈 Academic Focus Ratio")
                    mode_counts = df["mode"].value_counts().to_dict()
                    total = sum(mode_counts.values())
                    ratio = round(100 * mode_counts.get("academic", 0) / total, 1) if total > 0 else 0
                    gauge = go.Figure(go.Indicator(
                        mode="gauge+number+delta",
                        value=ratio,
                        title={'text': "Academic Focus (%)"},
                        delta={'reference': 60, 'increasing': {'color': "red"}},
                        gauge={
                            'axis': {'range': [0, 100]},
                            'bar': {'color': "#B71C1C"},
                            'steps': [
                                {'range': [0, 40], 'color': "#C8E6C9"},
                                {'range': [40, 70], 'color': "#FFF59D"},
                                {'range': [70, 100], 'color': "#FFCDD2"}
                            ]
                        }
                    ))
                    st.plotly_chart(gauge, use_container_width=True)

                    # --- SENTIMENT ANALYSIS (TextBlob) ---
                    st.subheader("😊 Sentiment & Emotion Trends")

                    def get_sentiment_score(text):
                        return TextBlob(text).sentiment.polarity

                    df["sentiment"] = df["reply"].apply(get_sentiment_score)
                    df["date"] = df["timestamp"].dt.date
                    sentiment_df = df.groupby("date")["sentiment"].mean().reset_index()

                    line = px.line(sentiment_df, x="date", y="sentiment",
                                   title="Daily Average Sentiment",
                                   markers=True,
                                   line_shape="spline",
                                   color_discrete_sequence=["#FFD54F"])
                    line.add_hline(y=0, line_dash="dot", line_color="gray")
                    st.plotly_chart(line, use_container_width=True)

                    avg_sentiment = sentiment_df["sentiment"].mean()
                    if avg_sentiment < -0.2:
                        st.error("⚠️ You're showing signs of mental fatigue. Consider taking short breaks or reflection sessions.")
                    elif avg_sentiment < 0.1:
                        st.warning("😐 You might be feeling neutral or low energy. Try some mindfulness activities.")
                    else:
                        st.success("🌞 Great emotional balance! Keep up your healthy routine.")

                    # --- EMOTIONAL HEATMAP ---
                    st.subheader("🌡️ Emotion Frequency Map")

                    # mood_keywords = {
                    #     "tired": "burnout",
                    #     "exhausted": "burnout",
                    #     "stressed": "burnout",
                    #     "anxious": "burnout",
                    #     "overwhelmed": "burnout",
                    #     "lazy": "procrastination",
                    #     "bored": "procrastination",
                    #     "distracted": "procrastination",
                    #     "motivated": "focus",
                    #     "calm": "balance",
                    #     "happy": "balance"
                    # }
                    
                    def detect_mood(text):
                        text_lower = text.lower()
                        polarity = TextBlob(text_lower).sentiment.polarity

                        # Core detection logic
                        if any(word in text_lower for word in ["tired", "stressed", "anxious", "overwhelmed", "drained"]):
                            return "burnout"
                        elif any(word in text_lower for word in ["lazy", "bored", "distracted", "procrastinate"]):
                            return "procrastination"
                        elif polarity < -0.3:
                            return "burnout"
                        elif polarity > 0.3:
                            return "balance"
                        else:
                            return "neutral"

                    df["mood"] = df["reply"].apply(detect_mood)
                    mood_pivot = df.groupby(["mood", df["timestamp"].dt.date]).size().reset_index(name="count")

                    if not mood_pivot.empty:
                        heat = px.density_heatmap(
                            mood_pivot, x="timestamp", y="mood", z="count",
                            title="Mood Frequency Over Time",
                            color_continuous_scale="RdYlGn_r"
                        )
                        st.plotly_chart(heat, use_container_width=True)

                        # --- Insight from mood categories ---
                        burnout_ratio = len(df[df["mood"] == "burnout"]) / len(df)
                        procrastination_ratio = len(df[df["mood"] == "procrastination"]) / len(df)

                        if burnout_ratio > 0.25:
                            st.error("🔥 Burnout Alert: Over 25% of recent sessions show stress/fatigue indicators.")
                        elif procrastination_ratio > 0.2:
                            st.warning("💤 Procrastination Trend: You're mentioning boredom or distractions frequently.")
                        else:
                            st.info("💚 Mood seems balanced. No strong burnout or procrastination trends detected.")

                    # --- REFLECTION SUMMARY ---
                    st.subheader("🪞 Reflect on Your Week")
                    if st.button("Generate Reflection Summary"):
                        try:
                            reflection_query = f"""
                            You are MedPal, the AI assistant, writing a wellness reflection **for the user named Buddy (the student)**. 
                            Reflect on their recent week using the following data:
                            - Academic to wellness ratio: {ratio}% academic
                            - Average sentiment: {avg_sentiment:.2f}
                            - Burnout frequency: {burnout_ratio:.2f}
                            - Procrastination frequency: {procrastination_ratio:.2f}

                            Provide a concise, emotionally intelligent reflection written *to Buddy*, addressing them in the second person (e.g., “you seem”, “your week shows”), 
                            and avoid saying “MedPal” in the response.
                            """

                            res = requests.post(API_URL, json={"query": reflection_query, "mode": "wellness"})
                            if res.status_code == 200:
                                reflection = res.json().get("reply", "")
                                st.success("✨ Your Reflection:")
                                st.markdown(reflection)
                            else:
                                st.error("Failed to generate reflection summary.")
                        except Exception as e:
                            st.error(f"Reflection request failed: {e}")

            else:
                st.info("No data yet. Chat with MedPal to see your insights.")
        except Exception as e:
            st.error(f"Could not load insights: {e}")
    else:
        st.info("No interactions recorded yet.")

# ----------------------------
# TAB 3 – STUDY DECK
# ----------------------------
with tab3:
    st.title("🎓 Study Deck – Review Your Flashcards")
    os.makedirs("data", exist_ok=True)
    if os.path.exists(DECK_PATH):
        try:
            deck = json.load(open(DECK_PATH))
        except json.JSONDecodeError:
            deck = []
    else:
        deck = []

    if not deck:
        st.info("No flashcards saved yet. Generate some in the Chat tab!")
    else:
        topics = sorted(set(d["topic"] for d in deck))
        topic = st.selectbox("📘 Select topic", ["All Topics"] + topics)
        if topic != "All Topics":
            cards = [c for c in deck if c["topic"] == topic]
        else:
            cards = deck

        if st.button("🔀 Shuffle Deck"):
            import random
            random.shuffle(cards)

        mastered_count = sum(1 for c in cards if c["mastered"])
        st.caption(f"⭐ Mastered {mastered_count}/{len(cards)} cards")

        for i, card in enumerate(cards):
            st.markdown(f"🧠 {card['front']}")
            with st.expander("Show Answer"):
                st.write(card["back"])
                if st.checkbox("Mark as Mastered", key=f"m_{i}", value=card["mastered"]):
                    card["mastered"] = True

        if st.button("💾 Save Progress"):
            json.dump(deck, open(DECK_PATH, "w"), indent=2)
            st.success("Progress saved!")

        if st.button("🗑️ Reset Mastery"):
            for c in deck: c["mastered"] = False
            json.dump(deck, open(DECK_PATH, "w"), indent=2)
            st.warning("All mastery progress reset!")

import os, json, time
from flask import Flask, request, jsonify
from backend.gemini_client import call_gemini
from backend.engines.academic.core import academic_engine
from backend.engines.wellness.core import wellness_engine
from textblob import TextBlob

app = Flask(__name__)
MEMORY_PATH = "backend/memory.json"

# ----------------------------------------
# Helper Functions
# ----------------------------------------
def load_context():
    if not os.path.exists(MEMORY_PATH):
        return {"sessions": []}
    try:
        data = json.load(open(MEMORY_PATH))
        if "sessions" not in data:
            data["sessions"] = []
        return data
    except json.JSONDecodeError:
        return {"sessions": []}


def save_context(ctx):
    with open(MEMORY_PATH, "w") as f:
        json.dump(ctx, f, indent=2)


def summarize_memory(ctx, limit=3):
    """Return a short text summary of the last few exchanges."""
    history = ctx.get("sessions", [])[-limit:]
    summary = ""
    for msg in history:
        summary += f"[{msg['timestamp']}] ({msg['mode']}) {msg['query']} → {msg['reply'][:120]}...\n"
    return summary.strip()


# ----------------------------------------
# Improved Mode Detection (Semantic)
# ----------------------------------------
def detect_mode(query: str):
    """
    Uses Gemini to classify user intent more accurately between Academic and Wellness.
    Prefers Wellness if the user expresses emotions, feelings, or requests reflection.
    """
    prompt = f"""
    You are an intent classifier for MedPal.
    Decide which category best fits this message:

    - academic → for studying, notes, exams, assignments, knowledge work, or productivity enhancement
    - wellness → for feelings, emotions, burnout, fatigue, motivation, self-reflection, or balance

    If both aspects appear, choose 'wellness' if the user expresses feelings or mentions reflection, stress, or emotions.
    Message: "{query}"

    Reply with only one word: academic or wellness.
    """

    try:
        intent = call_gemini(prompt, model="gemini-2.5-flash").strip().lower()
        if "wellness" in intent:
            return "wellness"
        elif "academic" in intent:
            return "academic"
        else:
            return "academic"
    except Exception as e:
        print(f"[Error in detect_mode]: {e}")
        return "academic"


# ----------------------------------------
# Main Route
# ----------------------------------------
@app.route("/query", methods=["POST"])
def handle_query():
    data = request.get_json()
    query = data.get("query", "")
    mode = data.get("mode", "auto")
    ctx = load_context()

    # Determine mode dynamically if set to auto
    if mode == "auto":
        last_mode = ctx.get("last_mode", "")
        detected = detect_mode(query)
        mode = detected if detected in ["academic", "wellness"] else last_mode or "academic"

    # Create context summary
    memory_summary = summarize_memory(ctx)
    ctx["memory_summary"] = memory_summary

    # Generate response
    if mode == "academic":
        reply = academic_engine(query, ctx)
    else:
        reply = wellness_engine(query, ctx)
    
    # --- Adaptive Wellness Advice Logic ---
    try:
        # Calculate academic ratio and sentiment trend from memory
        sessions = ctx.get("sessions", [])
        if sessions:
            total_sessions = len(sessions)
            academic_sessions = sum(1 for s in sessions if s["mode"] == "academic")
            recent_academic_ratio = (academic_sessions / total_sessions) * 100

            # Basic sentiment approximation
            sentiments = [TextBlob(s["reply"]).sentiment.polarity for s in sessions if s["reply"]]
            avg_sentiment = sum(sentiments) / len(sentiments) if sentiments else 0

            # Trigger advice if workload > 75% and mood dipping
            if mode == "academic" and recent_academic_ratio > 75 and avg_sentiment < 0:
                advice = (
                    "💡 **Wellness Tip:** You've been focusing heavily on academics lately "
                    f"({recent_academic_ratio:.1f}% of your interactions). "
                    "Take a short walk, stretch, or do a 5-minute mindful break — "
                    "your brain consolidates learning better with rest."
                )
                reply += "\n\n" + advice
    except Exception as e:
        print(f"[Adaptive Advice Error] {e}")


    # Log interaction
    ctx["last_mode"] = mode
    ctx["sessions"].append({
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        "mode": mode,
        "query": query,
        "reply": reply
    })

    # Limit memory size to avoid JSON bloat
    if len(ctx["sessions"]) > 20:
        ctx["sessions"] = ctx["sessions"][-20:]

    save_context(ctx)

    print(f"\n[MedPal Memory] Mode={mode.upper()} | Query={query}\n→ Reply: {reply[:150]}...\n")

    return jsonify({"reply": reply, "mode": mode})


if __name__ == "__main__":
    app.run(debug=True)

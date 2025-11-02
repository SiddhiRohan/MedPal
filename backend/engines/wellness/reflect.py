# Reflection Journal

from backend.gemini_client import call_gemini

def daily_reflection(context):
    """
    Generates a daily reflection summary based on recent wellness interactions.
    """
    sessions = context.get("sessions", [])[-5:]
    memory = context.get("memory_summary", "")
    last_mood = context.get("last_mood", "neutral")

    history = "\n".join([f"- {s['timestamp']}: {s['query']} ({s['mode']})" for s in sessions if s["mode"] == "wellness"])

    prompt = f"""
    You are MedPal Wellness Journal, summarizing the user's recent wellness interactions.

    Recent messages:
    {history or 'No recent wellness interactions.'}

    Past emotional context:
    {memory or 'No past context.'}

    Last known mood: {last_mood}

    Task:
    1️⃣ Write a short reflective summary (3–4 sentences) about the user’s week or recent feelings.
    2️⃣ Highlight patterns (e.g., "You’ve been anxious before exams, but also showing resilience").
    3️⃣ End with one motivational takeaway.
    """
    return call_gemini(prompt, model="gemini-2.5-flash")

from backend.gemini_client import call_gemini
from backend.engines.wellness.mood import analyze_mood
from backend.engines.wellness.habits import suggest_microhabit
from backend.engines.wellness.reflect import daily_reflection

def wellness_engine(query, context):
    """
    Routes wellness queries to the right sub-module.
    Handles mood detection, micro-habit tips, and reflection summaries.
    """
    q = query.lower().strip()
    memory = context.get("memory_summary", "")
    last_mood = context.get("last_mood", "neutral")

    # --- 1️⃣ Reflection Trigger ---
    if any(k in q for k in ["reflect", "journal", "summary", "how did i do"]):
        return daily_reflection(context)

    # --- 2️⃣ Micro-habit Advice ---
    elif any(k in q for k in ["tip", "habit", "advice", "suggestion", "improve"]):
        mood = analyze_mood(query)
        context["last_mood"] = mood
        return suggest_microhabit(mood, memory)

    # --- 3️⃣ Default: Empathetic Response + Mood Tracking ---
    else:
        mood = analyze_mood(query)
        context["last_mood"] = mood
        prompt = f"""
        You are **MedPal Wellness**, a supportive AI companion who remembers how the user has been feeling.

        Previous memory:
        {memory or 'No previous context.'}

        Detected mood: {mood}
        User message: "{query}"

        Respond empathetically, validate their feelings,
        and suggest one small, realistic action they can take now
        (e.g., walk, hydrate, breathe, stretch, message a friend).

        Keep your tone conversational and encouraging.
        End with one short positive affirmation.
        """
        return call_gemini(prompt, model="gemini-2.5-flash")

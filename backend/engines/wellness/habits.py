# Micro-Habit Recommender

from backend.gemini_client import call_gemini

def suggest_microhabit(mood, memory):
    """
    Suggests a simple, practical habit tailored to the user's mood.
    """
    prompt = f"""
    You are MedPal Wellness's Habit Coach.
    Based on the current mood ({mood}), suggest one or two realistic micro-habits
    that the user can do right now.

    Reference recent memory:
    {memory or 'No recent data.'}

    Follow these guidelines:
    • Make it simple (1-2 sentences).
    • Explain why it helps.
    • End with an uplifting reminder.

    Example:
    ---
    "Since you're feeling tired, step away for a 5-minute stretch and drink some water.
    It helps reset your mind. Small resets make big progress."
    ---

    Now suggest an appropriate micro-habit.
    """
    return call_gemini(prompt, model="gemini-2.5-flash")

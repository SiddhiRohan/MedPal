# Emotion Analysis

from backend.gemini_client import call_gemini

def analyze_mood(query):
    """
    Uses Gemini to detect emotional tone in the user's message.
    Returns a mood label (e.g., tired, anxious, calm, motivated).
    """
    prompt = f"""
    You are an emotion analyzer.
    Read this message and return only one of the following moods:
    tired, stressed, anxious, sad, calm, motivated, frustrated, or neutral.

    Message: "{query}"

    Respond with just the mood word.
    """
    result = call_gemini(prompt, model="gemini-2.5-flash").strip().lower()
    allowed = ["tired","stressed","anxious","sad","calm","motivated","frustrated","neutral"]
    return result if result in allowed else "neutral"

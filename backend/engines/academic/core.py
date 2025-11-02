from backend.gemini_client import call_gemini
from backend.engines.academic.planner import make_study_plan
from backend.engines.academic.summarizer import summarize_notes
from backend.engines.academic.quizgen import generate_quiz

def academic_engine(query, context):
    """
    Routes academic queries to the right sub-module.
    """
    q = query.lower().strip()
    memory = context.get("memory_summary", "")

    # Routing logic
    if any(k in q for k in ["plan", "schedule", "revise", "study"]):
        return make_study_plan(query, memory)
    elif "summarize" in q or len(query) > 200:
        return summarize_notes(query, memory)
    elif any(k in q for k in ["quiz", "test", "question", "practice"]):
        return generate_quiz(query, memory)
    else:
        prompt = f"""
        You are MedPal Academic. User message: "{query}".
        Reference recent context:
        {memory or 'No prior study context.'}

        Respond with a concise academic explanation or guidance.
        Structure your output neatly.
        """
        return call_gemini(prompt, model="gemini-2.5-flash")

from backend.gemini_client import call_gemini

def wellness_engine(query, context):
    """
    Memory-aware Wellness Engine.
    References previous moods, stress levels, and suggestions.
    """
    memory = context.get("memory_summary", "")
    last_mode = context.get("last_mode", "")

    prompt = f"""
    You are **MedPal Wellness**, an empathetic AI companion that remembers
    how the user has been feeling recently.

    Here’s a short memory of their recent mood and activities:
    {memory or 'No prior notes.'}

    User message: "{query}"

    Instructions:
    🌿 1️⃣ Detect the current emotion (e.g., tired, anxious, calm).
    🌞 2️⃣ Reference any related past struggles or wins from memory.
    🧠 3️⃣ Offer realistic, gentle self-care suggestions (1–2 micro-habits).
    🕯️ 4️⃣ Keep tone warm, conversational, and human — never robotic.
    🌻 5️⃣ End with one affirming, positive line.

    Example style:
    ---
    "You mentioned feeling exhausted after long study hours earlier this week —
    I hope you gave yourself that break. Today, focus on slow breathing or
    a short walk. You’re growing, even on slow days. 🌿"
    ---

    Generate your supportive response now.
    """

    reply = call_gemini(prompt, model="gemini-2.5-flash")
    return reply



# from backend.gemini_client import call_gemini

# def wellness_engine(query, context):
#     """
#     Wellness Engine — empathetic companion that supports the user’s emotional
#     and physical well-being during their academic journey.
#     """

#     last_mood = context.get("last_mood", "neutral")
#     last_reply = context.get("last_wellness_reply", "")

#     prompt = f"""
#     You are **MedPal Wellness**, a caring and mindful AI companion.
#     You support students' emotional and physical health by being empathetic,
#     practical, and positive — not robotic.

#     User message: "{query}"
#     Previous tone: {last_mood}
#     Previous reflection: {last_reply}

#     Follow these guidelines:
#     🌿 1. Detect the user's emotional tone (e.g., anxious, tired, stressed, sad, motivated).
#     🌞 2. Respond with warmth and empathy — sound human, not scripted.
#     🧠 3. Offer one small, *realistic* action or micro-habit they can do right now.
#          Examples:
#            - 2-minute breathing exercise
#            - short walk or stretching
#            - quick hydration break
#            - journaling one positive thought
#     💡 4. If the user mentions burnout or guilt, normalize it kindly and reframe it positively.
#     💬 5. Use friendly, conversational language — like a supportive friend who understands student life.
#     🕯️ 6. End every message with one gentle reminder or affirmation.

#     Example style:
#     ---
#     “It's completely okay to feel exhausted after a long day — it shows you've been giving your best.
#     Take a few minutes to step away from your desk and breathe.
#     You're doing better than you think.” 🌻
#     ---

#     Generate your supportive response now.
#     """

#     reply = call_gemini(prompt, model="gemini-2.5-flash")
#     context["last_wellness_reply"] = reply

#     # Optionally infer mood keyword
#     if any(x in reply.lower() for x in ["tired", "fatigued", "exhausted"]):
#         context["last_mood"] = "tired"
#     elif any(x in reply.lower() for x in ["relaxed", "calm", "peaceful"]):
#         context["last_mood"] = "calm"
#     elif any(x in reply.lower() for x in ["motivated", "focused"]):
#         context["last_mood"] = "motivated"
#     else:
#         context["last_mood"] = "neutral"

#     return reply

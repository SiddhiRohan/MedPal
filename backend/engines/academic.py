from backend.gemini_client import call_gemini

def academic_engine(query, context):
    """
    Memory-aware Academic Engine.
    Adapts based on previous academic sessions or topics.
    """
    memory = context.get("memory_summary", "")
    last_mode = context.get("last_mode", "")

    prompt = f"""
    You are **MedPal Academic**, a focused and supportive academic mentor.

    Here’s a short memory of recent interactions:
    {memory or 'No previous data.'}

    User message: "{query}"

    Instructions:
    1️⃣ Identify if user wants a plan, summary, or strategy.
    2️⃣ If similar topic appeared before, mention continuity
       (e.g., "Yesterday you studied anatomy — let's build on that.").
    3️⃣ Provide clear, structured advice (bullet points or day-wise schedule).
    4️⃣ Keep tone professional but encouraging.
    5️⃣ End with one motivating line.

    Example:
    ---
    📚 **Anatomy Revision Plan – Continuation**
    • Morning: Review upper limb diagrams
    • Afternoon: Focus on nerves and vessels
    • Evening: Quick quiz + rest

    💡 Keep momentum going — consistent effort pays off.
    ---

    Generate your response now.
    """

    reply = call_gemini(prompt, model="gemini-2.5-flash")
    return reply



# from backend.gemini_client import call_gemini

# def academic_engine(query, context):
#     """
#     Academic Engine — provides structured, intelligent, and concise academic guidance.
#     Handles:
#         - Study planning
#         - Concept summaries
#         - Exam preparation
#         - Note organization
#     """

#     last_mode = context.get("last_mode", "")
#     last_summary = context.get("last_academic_summary", "")

#     prompt = f"""
#     You are **MedPal Academic**, a focused and supportive AI assistant
#     that helps medical and college students study smarter.

#     Context summary (if any): {last_summary}

#     User query: "{query}"

#     Follow these rules:
#     1. Identify if the user is asking for:
#         - Study plan / schedule
#         - Summary / explanation of topics
#         - Revision strategy
#         - Memory tips
#         - Productivity advice
#     2. Structure the output cleanly with short sections or bullet points.
#     3. Give concrete steps, not generic advice.
#     4. Include *one line* of motivation or encouragement at the end.
#     5. If it's a planning task, suggest time blocks (e.g., "Morning: Anatomy | Afternoon: Physiology").
#     6. Avoid long essays — be concise, clear, and actionable.

#     Example output:
#     ---
#     🩺 **3-Day Anatomy Revision Plan**
#     • Day 1: Upper Limb — 3 hrs (Morning), Self-quiz (Evening)
#     • Day 2: Thorax — 2 hrs, diagrams + flashcards
#     • Day 3: Abdomen — 3 hrs + 30-min cumulative test

#     💡 Tip: Reward yourself after completing each block — consistency beats intensity.
#     ---

#     Generate your response now based on the user’s query.
#     """

#     reply = call_gemini(prompt, model="gemini-2.5-flash")
#     context["last_academic_summary"] = reply
#     return reply


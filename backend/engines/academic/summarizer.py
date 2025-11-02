# Concept Summarizer

from backend.gemini_client import call_gemini

def summarize_notes(query, memory):
    """
    Summarizes long text or lecture notes into concise bullet points.
    """
    prompt = f"""
    You are **MedPal Summarizer**, an AI for condensing complex notes
    into clear, high-yield summaries for exams.

    Reference (memory or previous topic): {memory or 'None'}

    Task:
    1️⃣ Read the following content or topic description.
    2️⃣ Generate a short, structured summary.
    3️⃣ Highlight key terms, formulas, or mechanisms.
    4️⃣ End with one exam tip or recall mnemonic if relevant.

    User content:
    {query}

    Output format:
    ---
    📚 **Summary**
    • Key point 1  
    • Key point 2  
    • Key point 3  

    🧩 **Exam Tip:** Remember the “ABC” rule for differentiating conditions.
    ---
    """
    return call_gemini(prompt, model="gemini-2.5-flash")

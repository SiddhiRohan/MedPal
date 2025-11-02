# Quiz / Flashcard Generator

from backend.gemini_client import call_gemini

def generate_quiz(query, memory):
    """
    Generates structured flashcards (Front/Back) for interactive use.
    """
    prompt = f"""
    You are MedPal Flashcard Creator.
    Generate 5–8 concise flashcards (front/back) on the given topic.

    Output format:
    Flashcard 1
    Front: ...
    Back: ...

    Flashcard 2
    Front: ...
    Back: ...
    ---
    Topic: "{query}"
    Context: {memory or 'No prior context.'}
    """
    return call_gemini(prompt, model="gemini-2.5-flash")


# from backend.gemini_client import call_gemini

# def generate_quiz(query, memory):
#     """
#     Generates 3-5 short quiz or flashcard questions for quick self-testing.
#     """
#     prompt = f"""
#     You are **MedPal Quiz Master**, a friendly AI that helps students test
#     their understanding with short, high-yield questions.

#     Use this prior study context:
#     {memory or 'No context provided.'}

#     User request: "{query}"

#     Rules:
#     1️⃣ If the user provides a topic, generate 3-5 single-sentence questions.
#     2️⃣ Give answers after a separator line.
#     3️⃣ Make them recall-based, not too open-ended.
#     4️⃣ End with one motivational line.

#     Example:
#     ---
#     🧪 **Microbiology Quick Quiz**
#     1. What stain is used for Mycobacterium tuberculosis?  
#     2. Which virus has a reverse transcriptase enzyme?  
#     3. What is the incubation period of Hepatitis A?

#     ---
#     ✅ **Answers**
#     1. Ziehl-Neelsen stain  
#     2. Retroviruses (e.g., HIV)  
#     3. 15–50 days

#     💡 Keep challenging yourself — repetition is mastery.
#     ---
#     """
#     return call_gemini(prompt, model="gemini-2.5-flash")

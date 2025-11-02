import os
from dotenv import load_dotenv
import google.generativeai as genai

# Load environment variables from .env
load_dotenv()

genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

def call_gemini(prompt, model="gemini-2.5-flash"):
    model = genai.GenerativeModel(model)
    response = model.generate_content(prompt)
    return response.text
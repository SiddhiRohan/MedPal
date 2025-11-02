from dotenv import load_dotenv
import os
import google.generativeai as genai

# Load API key from .env
load_dotenv()
api_key = os.getenv("GOOGLE_API_KEY")

if not api_key:
    print("❌ API key not found. Make sure your .env file is in the project root.")
    exit()

# Configure Gemini
genai.configure(api_key=api_key)

# Create model instance
model = genai.GenerativeModel("gemini-2.5-flash")

# Send a test prompt
response = model.generate_content("Say hello from MedPal 2.0!")
print("✅ Gemini Response:")
print(response.text)

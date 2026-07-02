import os
from dotenv import load_dotenv
import google.generativeai as genai

# Load .env
load_dotenv()
api_key = os.getenv("GOOGLE_API_KEY")

print(f"Loaded API key prefix: {api_key[:10] if api_key else 'None'}")

# Configure generative AI
genai.configure(api_key=api_key)

try:
    # Using gemini-2.5-flash since gemini-1.5-flash is not available on this endpoint
    model = genai.GenerativeModel('gemini-2.5-flash')
    response = model.generate_content("Say hello")
    print("Response text:")
    print(response.text)
except Exception as e:
    print(f"Error occurred: {e}")

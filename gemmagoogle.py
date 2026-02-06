from google import genai

import os
from dotenv import load_dotenv
load_dotenv()

client = genai.Client(api_key=os.getenv('GEMMA_API'))

def ask(text):
    try:
        response = client.models.generate_content(
            model="gemma-3-27b-it", contents=text #gemini-2.5-flash
        )

        return response.text
    except Exception as e:
        print(e)
        return "ERROR"
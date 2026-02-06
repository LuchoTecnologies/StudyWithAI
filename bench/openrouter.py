import requests
import json

import os
from dotenv import load_dotenv
load_dotenv()

def ask(text):
    response = requests.post(
    url="https://openrouter.ai/api/v1/chat/completions",
    headers={
        "Authorization": f"Bearer {os.getenv('OPENROUTERKEY')}",
        "HTTP-Referer": "<YOUR_SITE_URL>", # Optional. Site URL for rankings on openrouter.ai.
        "X-Title": "<YOUR_SITE_NAME>", # Optional. Site title for rankings on openrouter.ai.
    },
    data=json.dumps({
        "model": "deepseek/deepseek-r1-0528:free", # Optional
        "messages": [
        {
            "role": "user",
            "content": text
        }
        ]
    })
    )
    try:
        return response.json()["choices"][0]["message"]["content"]
    except:
        return "ERROR"

if __name__ == "__main__":
    print(ask(input("Ask openrouter: >>> ")))
import requests

import os
from dotenv import load_dotenv
load_dotenv()



def ask(input):
    response = requests.post(
        "https://apifreellm.com/api/v1/chat",
        headers={
            "Content-Type": "application/json",
            "Authorization": os.getenv('APIFREELLM')
        },
        json={
            "message": input
        }
    )

    resp = response.json()
    if resp["success"] == True:
        return resp["response"]
    else:
        print(resp["error"])
        return "ERROR"

if __name__ == "__main__":
    print(ask(input("Ask apifreellm: >>> ")))
import requests

print("Sending request")



def ask(input):
    response = requests.post(
        "https://apifreellm.com/api/v1/chat",
        headers={
            "Content-Type": "application/json",
            "Authorization": "Bearer apf_d7m5bmkkomji11h9l5itvq9j"
        },
        json={
            "message": input
        }
    )

    return response.json()["response"]
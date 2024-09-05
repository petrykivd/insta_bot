from fastapi import FastAPI
import requests

app = FastAPI()

ACCESS_TOKEN = "твій_instagram_access_token"
USER_ID = "твій_user_id"


@app.get("/direct_messages")
def get_direct_messages():
    url = f"https://graph.facebook.com/v17.0/{USER_ID}/conversations"

    params = {
        "access_token": ACCESS_TOKEN
    }

    response = requests.get(url, params=params)

    if response.status_code == 200:
        return response.json()
    else:
        return {"error": response.json()}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=5555)

from fastapi import FastAPI, Request, Response
from pydantic import BaseModel
import os
import requests

app = FastAPI()


# Модель для валідації вхідних даних
class WebhookRequest(BaseModel):
    object: str
    entry: list


# Ваш верифікаційний токен для вебхука і access token
VERIFY_TOKEN = os.getenv("VERIFY_TOKEN", "your_verify_token_here")
ACCESS_TOKEN = os.getenv("ACCESS_TOKEN", "your_access_token_here")


@app.get("/webhook")
async def verify_webhook(request: Request):
    mode = request.query_params.get("hub.mode")
    token = request.query_params.get("hub.verify_token")
    challenge = request.query_params.get("hub.challenge")

    if mode and token:
        if mode == "subscribe" and token == VERIFY_TOKEN:
            return Response(content=challenge, media_type="text/plain")
        else:
            return Response(status_code=403)


@app.post("/webhook")
async def webhook(request: Request, data: WebhookRequest):
    # Обробка вхідних даних
    if data.object == "instagram":
        for entry in data.entry:
            # Тут ви можете обробляти різні типи подій
            # Наприклад, нові коментарі, повідомлення тощо
            await process_instagram_update(entry)

    return {"success": True}


async def process_instagram_update(entry):
    # Приклад обробки оновлення
    # Ви можете адаптувати цю функцію відповідно до ваших потреб
    if "changes" in entry:
        for change in entry["changes"]:
            if change["field"] == "comments":
                comment = change["value"]
                await reply_to_comment(comment)


async def reply_to_comment(comment):
    # Приклад відповіді на коментар
    comment_id = comment["id"]
    media_id = comment["media"]["id"]
    message = "Дякуємо за ваш коментар!"

    url = f"https://graph.facebook.com/v12.0/{comment_id}/replies"
    params = {
        "access_token": ACCESS_TOKEN,
        "message": message
    }

    response = requests.post(url, params=params)
    if response.status_code == 200:
        print(f"Успішно відповіли на коментар {comment_id}")
    else:
        print(f"Помилка при відповіді на коментар: {response.text}")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
from fastapi import FastAPI, Request, HTTPException
from pydantic import BaseModel
import hmac
import hashlib

app = FastAPI()

# Конфігураційні змінні
VERIFY_TOKEN = "your_verify_token"  # Замініть на свій verify token
APP_SECRET = "your_app_secret"  # Секретний ключ для підпису запитів
REDIRECT_URI = "https://insaider.online:5555/instagram_redirect"
DATA_DELETION_URL = "https://insaider.online:5555/delete_data"


# 1. Верифікація вебхуку від Meta
@app.get("/webhook")
async def verify_webhook(request: Request):
    mode = request.query_params.get('hub.mode')
    token = request.query_params.get('hub.verify_token')
    challenge = request.query_params.get('hub.challenge')

    if mode == 'subscribe' and token == VERIFY_TOKEN:
        return challenge
    else:
        raise HTTPException(status_code=403, detail="Verification failed")


# 2. Обробка подій від вебхуків Meta
@app.post("/webhook")
async def receive_webhook(request: Request):
    signature = request.headers.get('X-Hub-Signature-256')
    body = await request.body()

    # Перевірка підпису вебхука
    if signature and verify_signature(APP_SECRET, body, signature):
        data = await request.json()
        print("Received webhook:", data)
        return {"status": "ok"}
    else:
        raise HTTPException(status_code=403, detail="Invalid signature")


# Допоміжна функція для перевірки підпису вебхуку
def verify_signature(app_secret, payload, signature):
    expected_signature = 'sha256=' + hmac.new(
        app_secret.encode(), payload, hashlib.sha256
    ).hexdigest()
    return hmac.compare_digest(expected_signature, signature)


# 3. Обробка бізнес-логіну через редирект
@app.get("/instagram_redirect")
async def instagram_redirect(code: str):
    # Тут ви можете обробити код для обміну на access token
    # Для цього зробіть запит на отримання токену від Meta
    return {"message": "Business login successful", "code": code}


# 4. Деавторизація користувача
@app.post("/deauthorize")
async def deauthorize(request: Request):
    data = await request.json()
    user_id = data.get("user_id")
    # Логіка для деактивації користувача
    return {"status": "user deauthorized", "user_id": user_id}


# 5. Видалення даних користувача
@app.post("/delete_data")
async def delete_data(request: Request):
    data = await request.json()
    user_id = data.get("user_id")
    # Логіка для видалення даних користувача
    return {"status": "user data deleted", "user_id": user_id}

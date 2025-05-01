import os
import schedule
import time
import requests
from datetime import datetime
from openai import OpenAI
import uuid
from dotenv import load_dotenv
import sys

# === ЗАГРУЗКА ПЕРЕМЕННЫХ ===
load_dotenv()

VK_TOKEN = os.getenv("VK_TOKEN")
GROUP_ID = int(os.getenv("VK_GROUP_ID", "-224615724"))
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Проверка ключей
if not OPENAI_API_KEY:
    raise ValueError("❌ OPENAI_API_KEY не найден. Убедитесь, что он указан в .env или в настройках Render.")
if not VK_TOKEN:
    raise ValueError("❌ VK_TOKEN не найден. Убедитесь, что он указан в .env или в настройках Render.")

# === ТЕКСТ ПОСТА ===
def generate_post_text():
    client = OpenAI(api_key=OPENAI_API_KEY)

    response = client.chat.completions.create(
        model="gpt-4",
        messages=[
            {
                "role": "user",
                "content": (
                    "Сгенерируй короткий (до 300 символов) экспертно-деловой пост для барбершопа "
                    "на одну из тем: свободные окна, работы, советы, скидки, запись открыта. "
                    "В конце обязательно добавь:\n"
                    "📞 +7 (900) 390-30-00\n🔗 @club224615724 (Онлайн - Запись)"
                    "пост должен быть аккуратно написан учитывая прафила инфографике в сообществе ВК"
                )
            }
        ],
        temperature=0.9,
        max_tokens=300
    )

    return response.choices[0].message.content

# === ИЗОБРАЖЕНИЕ ===
def download_placeholder_image():
    client = OpenAI(api_key=OPENAI_API_KEY)
    prompt = "барбершоп в живых цветах, мужская атмосфера, кресло, парикмахер работает, современный стиль, фокус на детали, реализм, яркий свет, без текста"

    response = client.images.generate(
        model="dall-e-3",
        prompt=prompt,
        size="1024x1024",
        quality="standard",
        n=1
    )

    image_url = response.data[0].url
    image_data = requests.get(image_url).content
    filename = f"barber_image_{uuid.uuid4()}.png"

    with open(filename, "wb") as f:
        f.write(image_data)

    return filename

# === ЗАГРУЗКА ФОТО ===
def upload_photo_to_vk(image_path):
    upload_url = requests.get(
        "https://api.vk.com/method/photos.getWallUploadServer",
        params={
            "access_token": VK_TOKEN,
            "v": "5.199",
            "group_id": abs(GROUP_ID)
        }
    ).json()["response"]["upload_url"]

    with open(image_path, "rb") as file:
        response = requests.post(upload_url, files={"photo": file}).json()

    save_photo = requests.get(
        "https://api.vk.com/method/photos.saveWallPhoto",
        params={
            "access_token": VK_TOKEN,
            "v": "5.199",
            "group_id": abs(GROUP_ID),
            "photo": response["photo"],
            "server": response["server"],
            "hash": response["hash"]
        }
    ).json()
    photo = save_photo["response"][0]
    return f'photo{photo["owner_id"]}_{photo["id"]}'

# === ПУБЛИКАЦИЯ ===
def publish_post():
    print(f"[{datetime.now()}] Генерация поста...")
    try:
        text = generate_post_text()
        image_path = download_placeholder_image()
        attachment = upload_photo_to_vk(image_path)

        response = requests.get(
            "https://api.vk.com/method/wall.post",
            params={
                "access_token": VK_TOKEN,
                "v": "5.199",
                "owner_id": GROUP_ID,
                "message": text,
                "attachments": attachment
            }
        ).json()

        if "response" in response:
            print(f"[{datetime.now()}] ✅ Пост опубликован!")
        else:
            print(f"[{datetime.now()}] ❌ Ошибка публикации:", response)
    except Exception as e:
        print(f"❌ Ошибка при публикации: {e}")

# === ЗАПУСК ===
if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else ""
    if cmd == "post":
        publish_post()
    elif cmd == "loop":
        print("♻️ Запуск ежедневного автоцикла публикаций...")
        schedule.every().day.at("09:00").do(publish_post)
        while True:
            schedule.run_pending()
            time.sleep(1)
    else:
        print("❓ Укажите аргумент: 'post' для публикации, 'loop' — для ежедневного запуска.")




import os
import praw
import openai
import requests

# Настройки Reddit
reddit = praw.Reddit(
    client_id=os.getenv("REDDIT_CLIENT_ID"),
    client_secret=os.getenv("REDDIT_CLIENT_SECRET"),
    username=os.getenv("REDDIT_USERNAME"),
    password=os.getenv("REDDIT_PASSWORD"),
    user_agent="assorti-bot by /u/" + os.getenv("REDDIT_USERNAME")
)

# Получение мема
def fetch_meme():
    subreddit = reddit.subreddit("memes")
    for post in subreddit.hot(limit=10):
        if not post.stickied and post.url.endswith(('.jpg', '.jpeg', '.png')):
            return post.title, post.url
    return None, None

# Генерация описания через GPT
def generate_caption(title):
    openai.api_key = os.getenv("OPENAI_API_KEY")
    prompt = f"Придумай короткий, смешной комментарий к мему с названием: \"{title}\" на русском языке."
    response = openai.ChatCompletion.create(
        model="gpt-4-turbo",
        messages=[{"role": "user", "content": prompt}]
    )
    return response.choices[0].message.content.strip()

# Публикация в ВК
def post_to_vk(caption, image_url):
    vk_token = os.getenv("VK_TOKEN")
    group_id = os.getenv("VK_GROUP_ID")  # Без знака минус

    # Загружаем фото
    upload_url = requests.get(
        "https://api.vk.com/method/photos.getWallUploadServer",
        params={
            "access_token": vk_token,
            "v": "5.199",
            "group_id": group_id
        }
    ).json()["response"]["upload_url"]

    image_data = requests.get(image_url).content
    files = {"photo": ("image.jpg", image_data)}
    upload_response = requests.post(upload_url, files=files).json()

    # Сохраняем фото на стену
    save_response = requests.get(
        "https://api.vk.com/method/photos.saveWallPhoto",
        params={
            "access_token": vk_token,
            "v": "5.199",
            "group_id": group_id,
            "photo": upload_response["photo"],
            "server": upload_response["server"],
            "hash": upload_response["hash"]
        }
    ).json()

    photo = save_response["response"][0]
    attachment = f'photo{photo["owner_id"]}_{photo["id"]}'

    # Публикуем пост
    requests.get(
        "https://api.vk.com/method/wall.post",
        params={
            "access_token": vk_token,
            "v": "5.199",
            "owner_id": f"-{group_id}",
            "message": caption,
            "attachments": attachment
        }
    )

# Главная функция
if __name__ == "__main__":
    title, image_url = fetch_meme()
    if title and image_url:
        print("🔹 Название:", title)
        print("🖼️ Ссылка на изображение:", image_url)
        caption = generate_caption(title)
        print("💬 GPT-описание:", caption)
        post_to_vk(caption, image_url)
    else:
        print("❌ Мем не найден.")

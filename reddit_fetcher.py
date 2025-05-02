import os
import requests
import openai
import praw

# Reddit API init
reddit = praw.Reddit(
    client_id=os.getenv("REDDIT_CLIENT_ID"),
    client_secret=os.getenv("REDDIT_CLIENT_SECRET"),
    username=os.getenv("REDDIT_USERNAME"),
    password=os.getenv("REDDIT_PASSWORD"),
    user_agent="assorti-bot by /u/" + os.getenv("REDDIT_USERNAME")
)

# OpenAI API key
openai.api_key = os.getenv("OPENAI_API_KEY")

def fetch_meme():
    subreddit = reddit.subreddit("memes")
    for post in subreddit.hot(limit=10):
        if post.url.endswith((".jpg", ".png", ".jpeg")):
            caption = post.title
            image_url = post.url
            gpt_caption = generate_caption(caption)
            print(f"🔷 Название: {caption}\n🖼️ Ссылка на изображение: {image_url}\n💬 GPT-описание: {gpt_caption}")
            post_to_vk(gpt_caption, image_url)
            break

def generate_caption(title):
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "Ты — весёлый комментатор мемов. Отвечай коротко и с юмором."},
                {"role": "user", "content": title}
            ]
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        print("❌ Ошибка GPT:", e)
        return title

def post_to_vk(caption, image_url):
    vk_token = os.getenv("VK_TOKEN")
    vk_group_id = os.getenv("VK_GROUP_ID")

    if not vk_token or not vk_group_id:
        print("❌ VK_TOKEN или VK_GROUP_ID не установлены.")
        return

    upload_server_url = "https://api.vk.com/method/photos.getWallUploadServer"
    upload_params = {
        "access_token": vk_token,
        "v": "5.131",
        "group_id": vk_group_id
    }

    upload_response = requests.get(upload_server_url, params=upload_params).json()
    print("📡 VK upload response:", upload_response)

    if "error" in upload_response:
        print("❌ Ошибка при получении upload_url:", upload_response["error"])
        return

    upload_url = upload_response["response"]["upload_url"]
    image_data = requests.get(image_url).content
    files = {"photo": ("image.jpg", image_data)}
    upload_result = requests.post(upload_url, files=files).json()
    print("📤 VK upload_result:", upload_result)

    if "server" not in upload_result:
        print("❌ Ошибка при загрузке изображения:", upload_result)
        return

    save_url = "https://api.vk.com/method/photos.saveWallPhoto"
    save_params = {
        "access_token": vk_token,
        "v": "5.131",
        "group_id": vk_group_id,
        "server": upload_result["server"],
        "photo": upload_result["photo"],
        "hash": upload_result["hash"]
    }

    save_response = requests.post(save_url, data=save_params).json()
    print("💾 VK save response:", save_response)

    if "response" not in save_response:
        print("❌ Ошибка при сохранении изображения:", save_response)
        return

    photo = save_response["response"][0]
    attachment = f'photo{photo["owner_id"]}_{photo["id"]}'

    post_url = "https://api.vk.com/method/wall.post"
    post_params = {
        "access_token": vk_token,
        "v": "5.131",
        "owner_id": f"-{vk_group_id}",
        "from_group": 1,
        "message": caption,
        "attachments": attachment
    }

    post_response = requests.post(post_url, data=post_params).json()
    print("✅ VK пост отправлен:", post_response)

# Запуск
if __name__ == "__main__":
    fetch_meme()

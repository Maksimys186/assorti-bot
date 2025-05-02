import os
import praw
import openai
import vk_api
import requests

# Reddit Auth
reddit = praw.Reddit(
    client_id=os.getenv("REDDIT_CLIENT_ID"),
    client_secret=os.getenv("REDDIT_CLIENT_SECRET"),
    username=os.getenv("REDDIT_USERNAME"),
    password=os.getenv("REDDIT_PASSWORD"),
    user_agent="assorti-bot by /u/" + os.getenv("REDDIT_USERNAME")
)

# OpenAI Auth
openai.api_key = os.getenv("OPENAI_API_KEY")

# VK Auth
vk_session = vk_api.VkApi(token=os.getenv("VK_TOKEN"))
vk = vk_session.get_api()
GROUP_ID = int(os.getenv("VK_GROUP_ID"))

def fetch_meme():
    subreddit = reddit.subreddit("memes")
    for post in subreddit.hot(limit=10):
        if not post.stickied and post.url.endswith((".jpg", ".png", ".jpeg")):
            return post.title, post.url
    return None, None

def generate_caption(title):
    prompt = f"Придумай забавный комментарий к мему с названием: \"{title}\". Сделай его коротким и смешным."
    response = openai.ChatCompletion.create(
        model="gpt-4-turbo",
        messages=[{"role": "user", "content": prompt}]
    )
    return response.choices[0].message.content.strip()

def download_image(url, filename='temp.jpg'):
    response = requests.get(url)
    with open(filename, 'wb') as f:
        f.write(response.content)
    return filename

def post_to_vk(image_path, title, caption):
    upload = vk_api.VkUpload(vk_session)
    photo = upload.photo_wall(photos=image_path, group_id=GROUP_ID)
    attachment = f'photo{photo[0]["owner_id"]}_{photo[0]["id"]}'
    vk.wall.post(
        owner_id=-GROUP_ID,
        message=f"📦 {title}\n💬 {caption}",
        attachments=attachment
    )

if __name__ == "__main__":
    title, image_url = fetch_meme()
    if title and image_url:
        print(f"Название: {title}")
        print(f"Ссылка на изображение: {image_url}")
        caption = generate_caption(title)
        print(f"GPT-описание: {caption}")
        image_path = download_image(image_url)
        post_to_vk(image_path, title, caption)


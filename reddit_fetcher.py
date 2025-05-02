import os
import openai
import praw
from reddit_config import reddit

# Установить ключ OpenAI
openai.api_key = os.getenv("OPENAI_API_KEY")

# Функция генерации комментария через GPT
def generate_caption(title):
    prompt = f"Придумай короткий и забавный комментарий к мему с заголовком: «{title}»"

    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",  # можно заменить на "gpt-3.5-turbo"
            messages=[
                {"role": "user", "content": prompt}
            ],
            temperature=0.8,
            max_tokens=60
        )
        return response['choices'][0]['message']['content'].strip()
    except Exception as e:
        print("❌ GPT ошибка:", e)
        return "🙂"

# Основная функция
def fetch_meme():
    try:
        subreddit = reddit.subreddit("memes")
        for post in subreddit.hot(limit=10):
            if post.url.endswith((".jpg", ".jpeg", ".png", ".gif")):
                title = post.title
                image_url = post.url
                caption = generate_caption(title)

                print("🔹 Название:", title)
                print("🖼 Ссылка на изображение:", image_url)
                print("💬 GPT-описание:", caption)
                print("-" * 60)
                break
    except Exception as e:
        print("❌ Ошибка Reddit:", e)

# Запуск
if __name__ == "__main__":
    fetch_meme()

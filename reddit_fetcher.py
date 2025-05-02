from reddit_config import reddit

def fetch_meme():
    subreddit = reddit.subreddit("memes")  # можно заменить на "funny", "dankmemes" и т.д.

    for post in subreddit.hot(limit=10):
        if not post.stickied and post.url.endswith(('.jpg', '.png', '.gif')):
            print("🔹 Название:", post.title)
            print("🖼️ Ссылка на изображение:", post.url)
            return post.title, post.url

    print("❌ Мем не найден.")
    return None, None

if __name__ == "__main__":
    fetch_meme()

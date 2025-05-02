import praw

reddit = praw.Reddit(
    client_id="ТВОЙ_CLIENT_ID",
    client_secret="ТВОЙ_CLIENT_SECRET",
    username="ТВОЙ_USERNAME",
    password="ТВОЙ_PASSWORD",
    user_agent="assorti-bot by /u/ТВОЙ_USERNAME"
)

subreddit = reddit.subreddit("funny")  # можно заменить на 'memes', 'dankmemes' и т.д.

for post in subreddit.hot(limit=10):
    if not post.stickied and post.url.endswith(('.jpg', '.png', '.gif')):
        print("Заголовок:", post.title)
        print("URL картинки:", post.url)
        break

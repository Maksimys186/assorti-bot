from dotenv import load_dotenv
import os

load_dotenv()

print("🔐 VK_TOKEN =", os.getenv("VK_TOKEN"))
print("👥 VK_GROUP_ID =", os.getenv("VK_GROUP_ID"))
print("🧠 OPENAI_API_KEY =", os.getenv("OPENAI_API_KEY"))

import os
from dotenv import load_dotenv

load_dotenv()

API_URL = os.getenv("API_URL", "https://api.siliconflow.cn/v1/chat/completions")
API_KEY = os.getenv("API_KEY", "sk-eisgfevoxkvnrqgubncjikuobqyohuzafrshvnmamtnobhzh")
FAST_MODEL = os.getenv("MODEL_NAME", "Qwen/Qwen2.5-7B-Instruct")

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data")

MAX_TOKENS = 3000
TIMEOUT = 60
TEMPERATURE = 0.3
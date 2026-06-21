import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv('BOT_TOKEN', '')
ADMIN_IDS = [int(x) for x in os.getenv('ADMIN_IDS', '').split(',') if x.strip()]
LOG_CHAT_ID = int(os.getenv('LOG_CHAT_ID', '0'))
VERIFY_TIMEOUT = int(os.getenv('VERIFY_TIMEOUT', '120'))
MAX_WARNS = int(os.getenv('MAX_WARNS', '3'))
BANNED_WORDS = [w.strip() for w in os.getenv('BANNED_WORDS', '').split(',') if w.strip()]
BAN_LINKS = os.getenv('BAN_LINKS', 'true').lower() == 'true'
BAN_FORWARDS = os.getenv('BAN_FORWARDS', 'false').lower() == 'true'
WELCOME_MSG = os.getenv('WELCOME_MSG', '👋 欢迎 {name} 加入群组！\n\n请在 {timeout} 秒内点击验证，否则将被移除。')
DB_PATH = os.getenv('DB_PATH', 'data/bot.db')

import json
import os
from pathlib import Path

CONFIG_PATH = os.getenv("CONFIG_PATH", "data/config.json")


def _load():
    path = Path(CONFIG_PATH)
    if not path.exists():
        raise FileNotFoundError(f"配置文件不存在: {CONFIG_PATH}")
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


_cfg = _load()

BOT_TOKEN = _cfg.get("bot_token", "")
ADMIN_IDS = _cfg.get("admin_ids", [])
LOG_CHAT_ID = _cfg.get("log_chat_id", 0)
VERIFY_TIMEOUT = _cfg.get("verify_timeout", 120)
MAX_WARNS = _cfg.get("max_warns", 3)
BANNED_WORDS = _cfg.get("banned_words", [])
BAN_LINKS = _cfg.get("ban_links", True)
BAN_FORWARDS = _cfg.get("ban_forwards", False)
WELCOME_MSG = _cfg.get("welcome_msg", "👋 欢迎 {name} 加入群组！\n\n请在 {timeout} 秒内点击验证，否则将被移除。")
PROXY = _cfg.get("proxy", "")
DB_CONFIG = _cfg.get("db", {"host": "127.0.0.1", "port": 3306, "user": "root", "password": "", "database": "tg-group-bot"})

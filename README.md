# 🤖 TG Group Bot

Telegram 群管机器人 - 图片验证码 + 广告过滤 + 自动管理

## ✨ 功能

- 🔐 **图片验证码** - 防机器人入群
- 🚫 **广告过滤** - 分级处理（警告/封禁）
- ⚠️ **警告系统** - 累计警告自动封禁
- 🔇 **禁言管理** - 支持定时禁言
- 👋 **欢迎消息** - 自定义欢迎语
- 📋 **日志记录** - 操作日志

## 🚀 部署

docker compose up -d --build

## ⚙️ 环境变量

| 变量 | 说明 |
|------|------|
| BOT_TOKEN | Bot Token |
| ADMIN_IDS | 管理员ID（逗号分隔） |
| LOG_CHAT_ID | 日志群ID |
| VERIFY_TIMEOUT | 验证超时（秒） |
| MAX_WARNS | 最大警告次数 |
| BANNED_WORDS | 敏感词（逗号分隔） |
| BAN_LINKS | 拦截链接 |

## 📦 技术栈

- Python 3.12
- python-telegram-bot
- Pillow（验证码生成）
- SQLite（数据存储）

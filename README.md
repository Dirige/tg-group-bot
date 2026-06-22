# 🤖 TG Group Bot

> 🛡️ Telegram 群管机器人 — 图片验证码 · 广告过滤 · 自动管理

[![Telegram](https://img.shields.io/badge/Telegram-交流反馈-blue?logo=telegram)](https://t.me/Dirige_Proxy)
[![GitHub](https://img.shields.io/badge/GitHub-源码-black?logo=github)](https://github.com/Dirige/tg-group-bot)
[![Docker](https://img.shields.io/badge/Docker-镜像-blue?logo=docker)](https://hub.docker.com/r/dirige/tg-group-bot)

---

## ✨ 功能一览

| 功能 | 说明 |
|------|------|
| 🔐 图片验证码 | 干扰线 + 噪点 + 6 个选项按钮，机器人根本过不去 |
| 🚫 广告过滤 | 分级处理：严重词直接封禁，一般词警告 |
| ⚠️ 警告系统 | 累计警告达上限自动封禁 |
| 🔇 禁言管理 | 支持定时禁言（30m / 1h / 1d） |
| 👋 欢迎消息 | 自定义欢迎语，可开关 |
| 📋 日志记录 | 所有操作私发给管理员 |
| 🧹 自动清理 | Bot 消息 3 分钟后自动删除 |

---

## 🚀 快速部署

### 1️⃣ 克隆项目
```bash
git clone https://github.com/Dirige/tg-group-bot.git
cd tg-group-bot
```

### 2️⃣ 配置环境变量
```bash
cp .env.example .env
nano .env
```

填写以下内容：
```env
# 从 @BotFather 获取
BOT_TOKEN=你的Bot_Token

# 从 @userinfobot 获取，多个用逗号分隔
ADMIN_IDS=123456789

# 验证超时（秒）
VERIFY_TIMEOUT=120

# 最大警告次数
MAX_WARNS=3

# 敏感词（逗号分隔）
BANNED_WORDS=赌博,色情,诈骗,刷单

# 是否拦截链接
BAN_LINKS=true
```

### 3️⃣ 启动
```bash
docker compose up -d --build
```

### 4️⃣ 查看日志
```bash
docker logs -f tg-group-bot
```

---

## ⚙️ 环境变量

| 变量 | 必填 | 说明 | 默认值 |
|:-----|:----:|------|:------:|
| `BOT_TOKEN` | ✅ | Bot Token | - |
| `ADMIN_IDS` | ✅ | 管理员 ID（逗号分隔） | - |
| `LOG_CHAT_ID` | ❌ | 日志群 ID，0 = 私发管理员 | `0` |
| `VERIFY_TIMEOUT` | ❌ | 验证超时（秒） | `120` |
| `MAX_WARNS` | ❌ | 最大警告次数 | `3` |
| `BANNED_WORDS` | ❌ | 敏感词（逗号分隔） | - |
| `BAN_LINKS` | ❌ | 拦截链接 | `true` |
| `BAN_FORWARDS` | ❌ | 拦截转发 | `false` |
| `DB_PATH` | ❌ | 数据库路径 | `data/bot.db` |

---

## 📖 命令列表

### 👤 用户管理

| 命令 | 说明 | 示例 |
|:-----|------|:-----|
| `/ban` | 🚫 封禁用户 | `/ban @spam_bot 发广告` |
| `/unban` | ✅ 解封用户 | `/unban @user` |
| `/kick` | 👢 踢出用户 | `/kick @user` |
| `/mute` | 🔇 禁言用户 | `/mute @user 30m` |
| `/unmute` | 🔊 解除禁言 | `/unmute @user` |
| `/warn` | ⚠️ 警告用户 | `/warn @user 违规` |
| `/unwarn` | 🔄 清除警告 | `/unwarn @user` |
| `/warns` | 📊 查看警告 | `/warns @user` |

### 📌 消息管理

| 命令 | 说明 | 示例 |
|:-----|------|:-----|
| `/pin` | 📌 置顶消息 | 回复消息后 `/pin` |
| `/unpin` | 📌 取消置顶 | `/unpin` |
| `/purge` | 🗑️ 批量删除 | `/purge 50` |

### ⚙️ 群组设置

| 命令 | 说明 |
|:-----|------|
| `/welcome` | 👋 开关欢迎消息 |
| `/verify` | 🔐 开关入群验证 |
| `/antispam` | 🛡️ 开关反垃圾 |
| `/settings` | ⚙️ 查看当前设置 |

---

## 🛡️ 防机器人机制

```
新人进群
   │
   ▼
┌─────────────────────────────┐
│  🔐 图片验证码 + 6个按钮     │
│  ┌───┐ ┌───┐ ┌───┐         │
│  │A3K│ │X7M│ │B9N│         │
│  └───┘ └───┘ └───┘         │
│  ┌───┐ ┌───┐ ┌───┐         │
│  │C2P│ │D5R│ │🔄│         │
│  └───┘ └───┘ └───┘         │
└─────────────────────────────┘
   │
   ├─ ✅ 点对 → 解禁 + 撤回验证码
   ├─ ❌ 点错 → 提示剩余次数
   ├─ ❌ 错 3 次 → 踢出
   └─ ⏰ 超时 → 踢出
```

---

## 📦 广告词库

### 🚨 严重词库（直接封禁）
| 类别 | 关键词 |
|------|--------|
| 赌博 | 博彩、彩票、百家乐、老虎机、六合彩 |
| 色情 | 约炮、裸聊、成人 |
| 诈骗 | 贷款、套现、信用卡、办证、发票 |

### ⚠️ 一般词库（警告）
| 类别 | 关键词 |
|------|--------|
| 营销 | 刷单、兼职、日赚、加微信、返利 |
| 引流 | 代理、招代理、加盟、推广 |
| 其他 | 脚本、外挂、VPN、代练 |

> 命中 3 个及以上一般词 → 升级为直接封禁

---

## 🔧 进阶配置

### 自定义敏感词
```env
BANNED_WORDS=赌博,色情,诈骗,刷单,兼职,日赚
```

### 开启转发拦截
```env
BAN_FORWARDS=true
```

### 修改验证超时
```env
VERIFY_TIMEOUT=180
```

---

## 📋 技术栈

| 组件 | 技术 |
|------|------|
| 语言 | Python 3.12 |
| 框架 | python-telegram-bot 21.x |
| 验证码 | Pillow |
| 数据库 | SQLite |
| 部署 | Docker / Docker Compose |

---

## 💬 交流反馈

有问题或建议？欢迎加入 Telegram 群组：

👉 **[@Dirige_Proxy](https://t.me/Dirige_Proxy)**

---

## 📄 开源协议

MIT License

---

> 🤖 由 [@Dirige](https://github.com/Dirige) 开发维护

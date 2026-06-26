# TG 群管机器人

Telegram 群组管理机器人：入群验证码 + 广告过滤 + 自动管理

## 功能

- **入群验证** — 图片验证码，6 选 1，点错 3 次踢出，超时踢出
- **广告过滤** — 严重违规（赌博/色情/诈骗）直接封禁，普通营销需 2 次命中才正式警告
- **管理命令** — ban/unban/kick/mute/unmute/warn/pin/purge 等
- **群组设置** — 欢迎消息、验证、反垃圾可独立开关
- **日志通知** — 所有操作自动通知管理员，附带操作按钮（清除警告 / 封禁用户）
- **可点击用户名** — 通知中的用户名可直接点击跳转

## 反垃圾机制

| 级别 | 关键词 | 处理方式 |
|------|--------|----------|
| 严重 (CRITICAL) | 赌博/色情/诈骗等 | 直接封禁 + 加入全局黑名单 |
| 警告 (WARNING) | 营销/引流/加好友等 | 2 次命中才正式警告，首次仅删除消息 |

## 部署

### 1. 克隆项目

```bash
git clone https://github.com/Dirige/tg-group-bot.git
cd tg-group-bot
```

### 2. 创建配置文件

```bash
mkdir -p data
cp config.example.json data/config.json
```

编辑 `data/config.json`，填写你的 Bot Token 和管理员 ID：

```json
{
  "bot_token": "你的Bot Token",
  "admin_ids": [你的Telegram ID],
  "log_chat_id": 0,
  "verify_timeout": 120,
  "max_warns": 3,
  "banned_words": [],
  "ban_links": true,
  "ban_forwards": false,
  "welcome_msg": "👋 欢迎 {name} 加入群组！\\n\\n请在 {timeout} 秒内点击验证，否则将被移除。",
  "proxy": ""
}
```

### 3. 启动

```bash
docker compose up -d --build
```

### 4. 查看日志

```bash
docker logs -f tg-group-bot
```

## 配置说明

| 字段 | 必填 | 说明 | 默认值 |
|------|------|------|--------|
| bot_token | 是 | Bot Token | - |
| admin_ids | 是 | 管理员 Telegram ID 列表 | - |
| log_chat_id | 否 | 日志群 ID，0 = 私发管理员 | 0 |
| verify_timeout | 否 | 验证超时（秒） | 120 |
| max_warns | 否 | 最大警告次数，达到后封禁 | 3 |
| banned_words | 否 | 自定义敏感词列表 | [] |
| ban_links | 否 | 拦截链接 | true |
| ban_forwards | 否 | 拦截转发消息 | false |
| welcome_msg | 否 | 欢迎消息模板，支持 {name} {timeout} | 默认模板 |
| proxy | 否 | 代理地址，如 socks5h://host:port | 空 |

## 命令

### 用户管理

| 命令 | 说明 |
|------|------|
| /ban | 封禁用户（回复消息或 /ban @用户 原因） |
| /unban | 解封用户 |
| /kick | 踢出用户（可重新入群） |
| /mute | 禁言（/mute @用户 30m） |
| /unmute | 解除禁言 |
| /warn | 警告（累计达上限自动封禁） |
| /unwarn | 撤销警告 |
| /warns | 查看警告次数 |

### 消息管理

| 命令 | 说明 |
|------|------|
| /pin | 置顶消息 |
| /unpin | 取消置顶 |
| /purge | 批量删除（/purge 10） |

### 群组设置

| 命令 | 说明 |
|------|------|
| /welcome | 开关欢迎消息 |
| /verify | 开关入群验证 |
| /antispam | 开关广告过滤 |
| /lock | 锁定群聊（新成员默认禁言） |
| /unlock | 解锁群聊 |
| /settings | 查看当前设置 |
| /blacklist | 查看全局黑名单 |
| /userinfo | 查看用户信息 |

## 管理员通知按钮

当触发广告警告时，日志通知会附带操作按钮：
- ✅ **清除警告** — 重置该用户的警告计数和命中计数
- 🚫 **封禁用户** — 直接封禁该用户

## 许可证

MIT License

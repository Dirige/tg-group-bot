# 🤖 TG Group Bot

Telegram 群管机器人 - 图片验证码 + 广告过滤 + 自动管理

## ✨ 功能特性

### 🔐 入群验证
- 图片验证码（4位字母数字 + 干扰线 + 噪点）
- 6个按钮选项（1个正确 + 5个干扰）
- 支持刷新验证码（最多3次）
- 点错3次自动踢出
- 超时自动踢出（可配置）
- 验证前禁言，验证通过后自动解禁
- 验证通过后自动撤回验证码消息

### 🚫 广告过滤
- **分级处理系统**
  - 严重违规（赌博/色情/诈骗）→ 直接封禁
  - 一般违规（营销/引流）→ 警告
  - 同时命中3+个关键词 → 直接封禁
- 零宽字符清洗（防止用特殊字符绕过检测）
- 链接拦截（可配置）
- 转发消息拦截（可配置）

### ⚠️ 警告系统
- 累计警告自动封禁
- 支持查看/清除警告
- 管理员可自定义最大警告次数

### 🔇 禁言管理
- 支持定时禁言（30m, 1h, 1d 等）
- 支持永久禁言
- 支持解除禁言

### 👋 欢迎消息
- 自定义欢迎语
- 可开关

### 📋 日志记录
- 所有操作私发给管理员
- 记录封禁、警告、踢出等操作

### 🧹 自动清理
- Bot 发送的消息 3 分钟后自动删除
- 保持群聊整洁

## 🚀 快速部署

### 1. 克隆仓库


### 2. 配置环境变量
复制  为  并填写配置：


编辑  文件：
TRIM_KERNEL_VERSION=6.18.18-trim
TRIM_SYS_VERSION=1.1.3107
SHLVL=0
TRIM_RUN_GID=947
HOME=/vol2/@appconf/com.dustinky.qwenpaw
TRIM_SYS_VERSION_MAJOR=1
TRIM_APPNAME=com.dustinky.qwenpaw
wizard_pypi_mirror=aliyun
TRIM_APPDEST_VOL=/vol2
PS1=(venv) 
LC_CTYPE=C.UTF-8
TRIM_RUN_USERNAME=com.dustinky.qwenpaw
TRIM_SYS_ARCH=x86
TRIM_RUN_GROUPNAME=com.dustinky.qwenpaw
TRIM_SERVICE_PORT=19091
TRIM_PKGMETA=/vol2/@appmeta/com.dustinky.qwenpaw
TRIM_DATA_ACCESSIBLE_PATHS=/vol2/1000/SSD2:/vol1/1000/SSD
TRIM_PKGHOME=/vol2/@apphome/com.dustinky.qwenpaw
_=/vol2/@apphome/com.dustinky.qwenpaw/venv/bin/python3
TRIM_PKGETC=/vol2/@appconf/com.dustinky.qwenpaw
TRIM_GID=947
TRIM_DATA_SHARE_PATHS=/vol2/@appshare/com.dustinky.qwenpaw
TRIM_SYS_VERSION_MINOR=1
TRIM_RUN_UID=952
PATH=/vol2/@apphome/com.dustinky.qwenpaw/venv/bin:/vol2/@apphome/com.dustinky.qwenpaw/venv/bin:/var/apps/nodejs_v24/target/bin:/usr/local/bin:/usr/local/sbin:/usr/bin:/usr/sbin:/bin:/sbin:.
wizard_log_level=info
QWENPAW_LOG_LEVEL=info
TRIM_TEMP_LOGFILE=/tmp/com.dustinky.qwenpaw.log.1860821441
QWENPAW_AUTH_ENABLED=true
TRIM_APPDEST=/vol2/@appcenter/com.dustinky.qwenpaw
TRIM_USERNAME=com.dustinky.qwenpaw
TRIM_GROUPNAME=com.dustinky.qwenpaw
TRIM_APP_STATUS=START
VIRTUAL_ENV_PROMPT=(venv) 
TRIM_PKGVAR=/vol2/@appdata/com.dustinky.qwenpaw
TRIM_UID=952
VIRTUAL_ENV=/vol2/@apphome/com.dustinky.qwenpaw/venv
QWENPAW_WORKING_DIR=/vol2/@appshare/com.dustinky.qwenpaw/.qwenpaw
TRIM_SYS_LANGUAGE=zh-CN
TRIM_APPVER=1.1.11
PWD=/vol2/@appshare/com.dustinky.qwenpaw/.qwenpaw/workspaces/default
TRIM_SYS_MACHINE_ID=f55e8a3608374114a4a2216538a0bfd335391cd9
TRIM_SYS_VERSION_BUILD=3107
TRIM_PKGTMP=/vol2/@apptemp/com.dustinky.qwenpaw

### 3. Docker 部署


### 4. 查看日志


## ⚙️ 环境变量说明

| 变量 | 必填 | 说明 | 默认值 |
|------|------|------|--------|
| BOT_TOKEN | ✅ | Bot Token | - |
| ADMIN_IDS | ✅ | 管理员 ID（逗号分隔） | - |
| LOG_CHAT_ID | ❌ | 日志群 ID（0=私发管理员） | 0 |
| VERIFY_TIMEOUT | ❌ | 验证超时（秒） | 120 |
| MAX_WARNS | ❌ | 最大警告次数 | 3 |
| BANNED_WORDS | ❌ | 敏感词（逗号分隔） | - |
| BAN_LINKS | ❌ | 拦截链接 | true |
| BAN_FORWARDS | ❌ | 拦截转发 | false |
| WELCOME_MSG | ❌ | 欢迎消息模板 | 默认模板 |
| DB_PATH | ❌ | 数据库路径 | data/bot.db |

## 📖 命令列表

### 👤 用户管理
| 命令 | 说明 | 示例 |
|------|------|------|
| /ban | 封禁用户 | /ban @用户 原因 |
| /unban | 解封用户 | /unban @用户 |
| /kick | 踢出用户 | /kick @用户 |
| /mute | 禁言用户 | /mute @用户 30m |
| /unmute | 解除禁言 | /unmute @用户 |
| /warn | 警告用户 | /warn @用户 原因 |
| /unwarn | 清除警告 | /unwarn @用户 |
| /warns | 查看警告 | /warns @用户 |

### 📌 消息管理
| 命令 | 说明 | 示例 |
|------|------|------|
| /pin | 置顶消息 | /pin（回复消息） |
| /unpin | 取消置顶 | /unpin |
| /purge | 批量删除 | /purge 10 |

### ⚙️ 群组设置
| 命令 | 说明 | 示例 |
|------|------|------|
| /welcome | 开关欢迎消息 | /welcome |
| /verify | 开关入群验证 | /verify |
| /antispam | 开关反垃圾 | /antispam |
| /settings | 查看设置 | /settings |

## 📦 广告词库

### 严重词库（直接封禁）
- 赌博：博彩、彩票、百家乐、老虎机、六合彩...
- 色情：约炮、裸聊、成人
- 诈骗：贷款、套现、信用卡、办证、发票

### 一般词库（警告）
- 营销：刷单、兼职、日赚、加微信、返利...
- 引流：代理、招代理、加盟、推广...
- 其他：脚本、外挂、VPN、代练...

## 🛡️ 防机器人特性

1. **图片验证码** - 机器人难以识别
2. **干扰线+噪点** - 防止 OCR 识别
3. **6个选项按钮** - 无法通过排除法
4. **点错限制** - 3次错误自动踢出
5. **刷新限制** - 最多3次刷新
6. **零宽字符清洗** - 防止用特殊字符绕过

## 🔧 高级配置

### 自定义敏感词
在  文件中添加 ：
TRIM_KERNEL_VERSION=6.18.18-trim
TRIM_SYS_VERSION=1.1.3107
SHLVL=0
TRIM_RUN_GID=947
HOME=/vol2/@appconf/com.dustinky.qwenpaw
TRIM_SYS_VERSION_MAJOR=1
TRIM_APPNAME=com.dustinky.qwenpaw
wizard_pypi_mirror=aliyun
TRIM_APPDEST_VOL=/vol2
PS1=(venv) 
LC_CTYPE=C.UTF-8
TRIM_RUN_USERNAME=com.dustinky.qwenpaw
TRIM_SYS_ARCH=x86
TRIM_RUN_GROUPNAME=com.dustinky.qwenpaw
TRIM_SERVICE_PORT=19091
TRIM_PKGMETA=/vol2/@appmeta/com.dustinky.qwenpaw
TRIM_DATA_ACCESSIBLE_PATHS=/vol2/1000/SSD2:/vol1/1000/SSD
TRIM_PKGHOME=/vol2/@apphome/com.dustinky.qwenpaw
_=/vol2/@apphome/com.dustinky.qwenpaw/venv/bin/python3
TRIM_PKGETC=/vol2/@appconf/com.dustinky.qwenpaw
TRIM_GID=947
TRIM_DATA_SHARE_PATHS=/vol2/@appshare/com.dustinky.qwenpaw
TRIM_SYS_VERSION_MINOR=1
TRIM_RUN_UID=952
PATH=/vol2/@apphome/com.dustinky.qwenpaw/venv/bin:/vol2/@apphome/com.dustinky.qwenpaw/venv/bin:/var/apps/nodejs_v24/target/bin:/usr/local/bin:/usr/local/sbin:/usr/bin:/usr/sbin:/bin:/sbin:.
wizard_log_level=info
QWENPAW_LOG_LEVEL=info
TRIM_TEMP_LOGFILE=/tmp/com.dustinky.qwenpaw.log.1860821441
QWENPAW_AUTH_ENABLED=true
TRIM_APPDEST=/vol2/@appcenter/com.dustinky.qwenpaw
TRIM_USERNAME=com.dustinky.qwenpaw
TRIM_GROUPNAME=com.dustinky.qwenpaw
TRIM_APP_STATUS=START
VIRTUAL_ENV_PROMPT=(venv) 
TRIM_PKGVAR=/vol2/@appdata/com.dustinky.qwenpaw
TRIM_UID=952
VIRTUAL_ENV=/vol2/@apphome/com.dustinky.qwenpaw/venv
QWENPAW_WORKING_DIR=/vol2/@appshare/com.dustinky.qwenpaw/.qwenpaw
TRIM_SYS_LANGUAGE=zh-CN
TRIM_APPVER=1.1.11
PWD=/vol2/@appshare/com.dustinky.qwenpaw/.qwenpaw/workspaces/default
TRIM_SYS_MACHINE_ID=f55e8a3608374114a4a2216538a0bfd335391cd9
TRIM_SYS_VERSION_BUILD=3107
TRIM_PKGTMP=/vol2/@apptemp/com.dustinky.qwenpaw

### 开启转发拦截
TRIM_KERNEL_VERSION=6.18.18-trim
TRIM_SYS_VERSION=1.1.3107
SHLVL=0
TRIM_RUN_GID=947
HOME=/vol2/@appconf/com.dustinky.qwenpaw
TRIM_SYS_VERSION_MAJOR=1
TRIM_APPNAME=com.dustinky.qwenpaw
wizard_pypi_mirror=aliyun
TRIM_APPDEST_VOL=/vol2
PS1=(venv) 
LC_CTYPE=C.UTF-8
TRIM_RUN_USERNAME=com.dustinky.qwenpaw
TRIM_SYS_ARCH=x86
TRIM_RUN_GROUPNAME=com.dustinky.qwenpaw
TRIM_SERVICE_PORT=19091
TRIM_PKGMETA=/vol2/@appmeta/com.dustinky.qwenpaw
TRIM_DATA_ACCESSIBLE_PATHS=/vol2/1000/SSD2:/vol1/1000/SSD
TRIM_PKGHOME=/vol2/@apphome/com.dustinky.qwenpaw
_=/vol2/@apphome/com.dustinky.qwenpaw/venv/bin/python3
TRIM_PKGETC=/vol2/@appconf/com.dustinky.qwenpaw
TRIM_GID=947
TRIM_DATA_SHARE_PATHS=/vol2/@appshare/com.dustinky.qwenpaw
TRIM_SYS_VERSION_MINOR=1
TRIM_RUN_UID=952
PATH=/vol2/@apphome/com.dustinky.qwenpaw/venv/bin:/vol2/@apphome/com.dustinky.qwenpaw/venv/bin:/var/apps/nodejs_v24/target/bin:/usr/local/bin:/usr/local/sbin:/usr/bin:/usr/sbin:/bin:/sbin:.
wizard_log_level=info
QWENPAW_LOG_LEVEL=info
TRIM_TEMP_LOGFILE=/tmp/com.dustinky.qwenpaw.log.1860821441
QWENPAW_AUTH_ENABLED=true
TRIM_APPDEST=/vol2/@appcenter/com.dustinky.qwenpaw
TRIM_USERNAME=com.dustinky.qwenpaw
TRIM_GROUPNAME=com.dustinky.qwenpaw
TRIM_APP_STATUS=START
VIRTUAL_ENV_PROMPT=(venv) 
TRIM_PKGVAR=/vol2/@appdata/com.dustinky.qwenpaw
TRIM_UID=952
VIRTUAL_ENV=/vol2/@apphome/com.dustinky.qwenpaw/venv
QWENPAW_WORKING_DIR=/vol2/@appshare/com.dustinky.qwenpaw/.qwenpaw
TRIM_SYS_LANGUAGE=zh-CN
TRIM_APPVER=1.1.11
PWD=/vol2/@appshare/com.dustinky.qwenpaw/.qwenpaw/workspaces/default
TRIM_SYS_MACHINE_ID=f55e8a3608374114a4a2216538a0bfd335391cd9
TRIM_SYS_VERSION_BUILD=3107
TRIM_PKGTMP=/vol2/@apptemp/com.dustinky.qwenpaw

### 修改验证超时
TRIM_KERNEL_VERSION=6.18.18-trim
TRIM_SYS_VERSION=1.1.3107
SHLVL=0
TRIM_RUN_GID=947
HOME=/vol2/@appconf/com.dustinky.qwenpaw
TRIM_SYS_VERSION_MAJOR=1
TRIM_APPNAME=com.dustinky.qwenpaw
wizard_pypi_mirror=aliyun
TRIM_APPDEST_VOL=/vol2
PS1=(venv) 
LC_CTYPE=C.UTF-8
TRIM_RUN_USERNAME=com.dustinky.qwenpaw
TRIM_SYS_ARCH=x86
TRIM_RUN_GROUPNAME=com.dustinky.qwenpaw
TRIM_SERVICE_PORT=19091
TRIM_PKGMETA=/vol2/@appmeta/com.dustinky.qwenpaw
TRIM_DATA_ACCESSIBLE_PATHS=/vol2/1000/SSD2:/vol1/1000/SSD
TRIM_PKGHOME=/vol2/@apphome/com.dustinky.qwenpaw
_=/vol2/@apphome/com.dustinky.qwenpaw/venv/bin/python3
TRIM_PKGETC=/vol2/@appconf/com.dustinky.qwenpaw
TRIM_GID=947
TRIM_DATA_SHARE_PATHS=/vol2/@appshare/com.dustinky.qwenpaw
TRIM_SYS_VERSION_MINOR=1
TRIM_RUN_UID=952
PATH=/vol2/@apphome/com.dustinky.qwenpaw/venv/bin:/vol2/@apphome/com.dustinky.qwenpaw/venv/bin:/var/apps/nodejs_v24/target/bin:/usr/local/bin:/usr/local/sbin:/usr/bin:/usr/sbin:/bin:/sbin:.
wizard_log_level=info
QWENPAW_LOG_LEVEL=info
TRIM_TEMP_LOGFILE=/tmp/com.dustinky.qwenpaw.log.1860821441
QWENPAW_AUTH_ENABLED=true
TRIM_APPDEST=/vol2/@appcenter/com.dustinky.qwenpaw
TRIM_USERNAME=com.dustinky.qwenpaw
TRIM_GROUPNAME=com.dustinky.qwenpaw
TRIM_APP_STATUS=START
VIRTUAL_ENV_PROMPT=(venv) 
TRIM_PKGVAR=/vol2/@appdata/com.dustinky.qwenpaw
TRIM_UID=952
VIRTUAL_ENV=/vol2/@apphome/com.dustinky.qwenpaw/venv
QWENPAW_WORKING_DIR=/vol2/@appshare/com.dustinky.qwenpaw/.qwenpaw
TRIM_SYS_LANGUAGE=zh-CN
TRIM_APPVER=1.1.11
PWD=/vol2/@appshare/com.dustinky.qwenpaw/.qwenpaw/workspaces/default
TRIM_SYS_MACHINE_ID=f55e8a3608374114a4a2216538a0bfd335391cd9
TRIM_SYS_VERSION_BUILD=3107
TRIM_PKGTMP=/vol2/@apptemp/com.dustinky.qwenpaw

### 修改最大警告次数
TRIM_KERNEL_VERSION=6.18.18-trim
TRIM_SYS_VERSION=1.1.3107
SHLVL=0
TRIM_RUN_GID=947
HOME=/vol2/@appconf/com.dustinky.qwenpaw
TRIM_SYS_VERSION_MAJOR=1
TRIM_APPNAME=com.dustinky.qwenpaw
wizard_pypi_mirror=aliyun
TRIM_APPDEST_VOL=/vol2
PS1=(venv) 
LC_CTYPE=C.UTF-8
TRIM_RUN_USERNAME=com.dustinky.qwenpaw
TRIM_SYS_ARCH=x86
TRIM_RUN_GROUPNAME=com.dustinky.qwenpaw
TRIM_SERVICE_PORT=19091
TRIM_PKGMETA=/vol2/@appmeta/com.dustinky.qwenpaw
TRIM_DATA_ACCESSIBLE_PATHS=/vol2/1000/SSD2:/vol1/1000/SSD
TRIM_PKGHOME=/vol2/@apphome/com.dustinky.qwenpaw
_=/vol2/@apphome/com.dustinky.qwenpaw/venv/bin/python3
TRIM_PKGETC=/vol2/@appconf/com.dustinky.qwenpaw
TRIM_GID=947
TRIM_DATA_SHARE_PATHS=/vol2/@appshare/com.dustinky.qwenpaw
TRIM_SYS_VERSION_MINOR=1
TRIM_RUN_UID=952
PATH=/vol2/@apphome/com.dustinky.qwenpaw/venv/bin:/vol2/@apphome/com.dustinky.qwenpaw/venv/bin:/var/apps/nodejs_v24/target/bin:/usr/local/bin:/usr/local/sbin:/usr/bin:/usr/sbin:/bin:/sbin:.
wizard_log_level=info
QWENPAW_LOG_LEVEL=info
TRIM_TEMP_LOGFILE=/tmp/com.dustinky.qwenpaw.log.1860821441
QWENPAW_AUTH_ENABLED=true
TRIM_APPDEST=/vol2/@appcenter/com.dustinky.qwenpaw
TRIM_USERNAME=com.dustinky.qwenpaw
TRIM_GROUPNAME=com.dustinky.qwenpaw
TRIM_APP_STATUS=START
VIRTUAL_ENV_PROMPT=(venv) 
TRIM_PKGVAR=/vol2/@appdata/com.dustinky.qwenpaw
TRIM_UID=952
VIRTUAL_ENV=/vol2/@apphome/com.dustinky.qwenpaw/venv
QWENPAW_WORKING_DIR=/vol2/@appshare/com.dustinky.qwenpaw/.qwenpaw
TRIM_SYS_LANGUAGE=zh-CN
TRIM_APPVER=1.1.11
PWD=/vol2/@appshare/com.dustinky.qwenpaw/.qwenpaw/workspaces/default
TRIM_SYS_MACHINE_ID=f55e8a3608374114a4a2216538a0bfd335391cd9
TRIM_SYS_VERSION_BUILD=3107
TRIM_PKGTMP=/vol2/@apptemp/com.dustinky.qwenpaw

## 📝 更新日志

### v1.0.0
- ✅ 图片验证码系统
- ✅ 分级广告过滤
- ✅ 零宽字符清洗
- ✅ 自动清理消息
- ✅ 日志私发管理员
- ✅ 验证前禁言
- ✅ 验证通过自动撤回

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

## 📄 许可证

MIT License

## 🔗 链接

- [GitHub](https://github.com/Dirige/tg-group-bot)
- [Docker Hub](https://hub.docker.com/r/dirige/tg-group-bot)

## 💬 支持

如有问题，请提交 Issue 或联系管理员。

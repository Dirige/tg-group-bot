import time
import logging
import asyncio
from datetime import datetime, timezone, timedelta
from telegram import Update, BotCommand, InlineKeyboardButton, InlineKeyboardMarkup, ChatPermissions, InputMediaPhoto
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, ChatMemberHandler, ChatJoinRequestHandler, ContextTypes, filters
from telegram.constants import ChatMemberStatus, ParseMode
import config
from database import Database
from filters import check_message
from captcha import generate_captcha, create_captcha_image, generate_fake_options

COMMANDS = [
    ("ban",     "封禁用户 - 回复消息或 /ban @用户 [原因]"),
    ("unban",   "解封用户 - 回复消息或 /unban @用户"),
    ("kick",    "踢出用户 - 回复消息或 /kick @用户（可重新入群）"),
    ("mute",    "禁言用户 - 回复消息或 /mute @用户 [时长] 例: 30m, 2h"),
    ("unmute",  "解除禁言 - 回复消息或 /unmute @用户"),
    ("warn",    "警告用户 - 回复消息或 /warn @用户 [原因]"),
    ("unwarn",  "撤销警告 - 回复消息或 /unwarn @用户"),
    ("warns",   "查看警告 - 回复消息或 /warns @用户"),
    ("pin",     "置顶消息 - 回复要置顶的消息"),
    ("unpin",   "取消置顶 - 回复已置顶的消息"),
    ("purge",   "批量删除 - 回复一条消息后 /purge 数量"),
    ("welcome", "设置欢迎语 - /welcome 文本内容（支持 {name} {mention}）"),
    ("verify",  "入群验证 - 开关新成员入群验证"),
    ("lock",    "锁定群聊 - 新成员默认禁言"),
    ("unlock",  "解锁群聊 - 恢复新成员发言权限"),
    ("antispam","广告过滤 - 开关自动广告检测和过滤"),
    ("settings","查看设置 - 显示当前群组的配置状态"),
    ("blacklist","查看黑名单 - /blacklist [关键词]"),
    ("userinfo","查看用户 - /userinfo 用户ID"),
    ("help",    "查看帮助 - 显示所有命令和说明"),
]

FULL_PERMISSIONS = ChatPermissions(
    can_send_messages=True, can_send_audios=True, can_send_documents=True,
    can_send_photos=True, can_send_videos=True, can_send_video_notes=True,
    can_send_voice_notes=True, can_send_other_messages=True, can_add_web_page_previews=True
)
MUTED_PERMISSIONS = ChatPermissions(
    can_send_messages=False, can_send_audios=False, can_send_documents=False,
    can_send_photos=False, can_send_videos=False, can_send_video_notes=False,
    can_send_voice_notes=False, can_send_other_messages=False,
    can_add_web_page_previews=False
)

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)
db = None

def is_admin(uid): return uid in config.ADMIN_IDS

async def check_admin(update, context):
    if is_admin(update.effective_user.id): return True
    try:
        m = await context.bot.get_chat_member(update.effective_chat.id, update.effective_user.id)
        return m.status in [ChatMemberStatus.OWNER, ChatMemberStatus.ADMINISTRATOR]
    except: return False

async def log_action(context, cid, action, user=None, reason=''):
    if not config.LOG_CHAT_ID: return
    try:
        chat = await context.bot.get_chat(cid)
        chat_name = chat.title or str(cid)
    except:
        chat_name = str(cid)
    t = f'📋 **{action}**\n群组: {chat_name} (`{cid}`)\n'
    if user:
        user_link = f'[{user.first_name}](tg://user?id={user.id})'
        t += f'用户: {user_link} (`{user.id}`)\n'
    if reason: t += f'原因: {reason}\n'
    cst = timezone(timedelta(hours=8))
    t += f'时间: {datetime.now(cst).strftime("%H:%M:%S")}'
    keyboard = None
    if user and '警告' in action:
        keyboard = InlineKeyboardMarkup([
            [
                InlineKeyboardButton('✅ 清除警告', callback_data=f'admin_unwarn:{cid}:{user.id}'),
                InlineKeyboardButton('🚫 封禁用户', callback_data=f'admin_ban:{cid}:{user.id}'),
            ]
        ])
    try: await context.bot.send_message(config.LOG_CHAT_ID, t, parse_mode=ParseMode.MARKDOWN, reply_markup=keyboard)
    except: pass

def parse_time(s):
    if not s: return None
    try:
        s = s.lower()
        if s.endswith('m'): return int(s[:-1]) * 60
        if s.endswith('h'): return int(s[:-1]) * 3600
        if s.endswith('d'): return int(s[:-1]) * 86400
        return int(s) * 60
    except (ValueError, IndexError):
        return None

def get_target(update, context):
    if update.message.reply_to_message: return update.message.reply_to_message.from_user.id
    if context.args:
        try: return int(context.args[0].replace('@', ''))
        except: pass
    return None

def get_target_time(update, context):
    if update.message.reply_to_message:
        return update.message.reply_to_message.from_user.id, (context.args[0] if context.args else None)
    if len(context.args) >= 2:
        try: return int(context.args[0].replace('@', '')), context.args[1]
        except: pass
    return None, None

def build_captcha_buttons(captcha_text, user_id, refresh_count=None):
    options = generate_fake_options(captcha_text, 5)
    buttons = []
    row = []
    for opt in options:
        tag = 'verify_ok' if opt == captcha_text else 'verify_fail'
        row.append(InlineKeyboardButton(opt, callback_data=f'{tag}:{user_id}'))
        if len(row) == 3:
            buttons.append(row)
            row = []
    if row:
        buttons.append(row)
    label = '🔄 换一张'
    if refresh_count is not None:
        label += f' ({3 - refresh_count})'
    buttons.append([InlineKeyboardButton(label, callback_data=f'verify_refresh:{user_id}')])
    return InlineKeyboardMarkup(buttons)

async def cmd_start(u, c):
    await u.message.reply_text('🤖 群管机器人\n/help 查看所有命令和说明')

async def cmd_help(u, c):
    lines = ['🤖 **群管机器人 - 命令列表**\n']
    for cmd, desc in COMMANDS:
        lines.append(f'`/{cmd}` - {desc}')
    lines.append('\n💡 提示：回复用户消息执行命令，或直接 @用户ID')
    await u.message.reply_text('\n'.join(lines), parse_mode=ParseMode.MARKDOWN)

async def post_init(app: Application):
    bot_commands = [BotCommand(cmd, desc) for cmd, desc in COMMANDS]
    await app.bot.set_my_commands(bot_commands)
    logger.info("Bot commands registered: %s", [c.command for c in bot_commands])

async def cmd_ban(u, c):
    if not await check_admin(u, c): return
    t = get_target(u, c)
    if not t: return await u.message.reply_text('❌ 指定用户')
    r = ' '.join(c.args[1:]) if len(c.args) > 1 else '无'
    await c.bot.ban_chat_member(u.effective_chat.id, t)
    msg = await u.message.reply_text('✅ 封禁 `' + str(t) + '`\n原因: ' + r, parse_mode=ParseMode.MARKDOWN)
    c.job_queue.run_once(lambda ctx: ctx.bot.delete_message(u.effective_chat.id, msg.message_id), 180)
    await log_action(c, u.effective_chat.id, '封禁', u.effective_user, r)

async def cmd_unban(u, c):
    if not await check_admin(u, c): return
    t = get_target(u, c)
    if not t: return await u.message.reply_text('❌ 指定用户')
    await c.bot.unban_chat_member(u.effective_chat.id, t)
    msg = await u.message.reply_text('✅ 解封 `' + str(t) + '`', parse_mode=ParseMode.MARKDOWN)
    c.job_queue.run_once(lambda ctx: ctx.bot.delete_message(u.effective_chat.id, msg.message_id), 180)

async def cmd_kick(u, c):
    if not await check_admin(u, c): return
    t = get_target(u, c)
    if not t: return await u.message.reply_text('❌ 指定用户')
    await c.bot.ban_chat_member(u.effective_chat.id, t)
    await asyncio.sleep(1)
    await c.bot.unban_chat_member(u.effective_chat.id, t)
    msg = await u.message.reply_text('✅ 踢出 `' + str(t) + '`', parse_mode=ParseMode.MARKDOWN)
    c.job_queue.run_once(lambda ctx: ctx.bot.delete_message(u.effective_chat.id, msg.message_id), 180)

async def cmd_mute(u, c):
    if not await check_admin(u, c): return
    t, ts = get_target_time(u, c)
    if not t: return await u.message.reply_text('❌ 指定用户')
    d = parse_time(ts)
    un = int(time.time() + d) if d else None
    await c.bot.restrict_chat_member(u.effective_chat.id, t, ChatPermissions(can_send_messages=False), until_date=un)
    db.add_mute(t, u.effective_chat.id, time.time() + d if d else 0)
    msg = await u.message.reply_text('🔇 禁言 `' + str(t) + '` ' + (ts or '永久'), parse_mode=ParseMode.MARKDOWN)
    c.job_queue.run_once(lambda ctx: ctx.bot.delete_message(u.effective_chat.id, msg.message_id), 180)

async def cmd_unmute(u, c):
    if not await check_admin(u, c): return
    t = get_target(u, c)
    if not t: return await u.message.reply_text('❌ 指定用户')
    await c.bot.restrict_chat_member(u.effective_chat.id, t, FULL_PERMISSIONS)
    db.remove_mute(t, u.effective_chat.id)
    msg = await u.message.reply_text('🔊 解禁 `' + str(t) + '`', parse_mode=ParseMode.MARKDOWN)
    c.job_queue.run_once(lambda ctx: ctx.bot.delete_message(u.effective_chat.id, msg.message_id), 180)

async def cmd_warn(u, c):
    if not await check_admin(u, c): return
    t = get_target(u, c)
    if not t: return await u.message.reply_text('❌ 指定用户')
    r = ' '.join(c.args[1:]) if len(c.args) > 1 else '无'
    n = db.add_warn(t, u.effective_chat.id)
    txt = '⚠️ `' + str(t) + '` 警告 (' + str(n) + '/' + str(config.MAX_WARNS) + ')\n原因: ' + r
    if n >= config.MAX_WARNS:
        await c.bot.ban_chat_member(u.effective_chat.id, t)
        db.reset_warns(t, u.effective_chat.id)
        txt += '\n🚫 已封禁'
    msg = await u.message.reply_text(txt, parse_mode=ParseMode.MARKDOWN)
    c.job_queue.run_once(lambda ctx: ctx.bot.delete_message(u.effective_chat.id, msg.message_id), 180)
    await log_action(c, u.effective_chat.id, '警告', u.effective_user, r + ' (' + str(n) + ')')

async def cmd_unwarn(u, c):
    if not await check_admin(u, c): return
    t = get_target(u, c)
    if not t: return await u.message.reply_text('❌ 指定用户')
    db.reset_warns(t, u.effective_chat.id)
    msg = await u.message.reply_text('✅ 已清除 `' + str(t) + '` 警告', parse_mode=ParseMode.MARKDOWN)
    c.job_queue.run_once(lambda ctx: ctx.bot.delete_message(u.effective_chat.id, msg.message_id), 180)

async def cmd_warns(u, c):
    t = get_target(u, c) or u.effective_user.id
    n = db.get_warns(t, u.effective_chat.id)
    msg = await u.message.reply_text('⚠️ `' + str(t) + '` 警告: ' + str(n) + '/' + str(config.MAX_WARNS), parse_mode=ParseMode.MARKDOWN)
    c.job_queue.run_once(lambda ctx: ctx.bot.delete_message(u.effective_chat.id, msg.message_id), 180)

async def cmd_pin(u, c):
    if not await check_admin(u, c): return
    if not u.message.reply_to_message: return await u.message.reply_text('❌ 回复消息')
    await c.bot.pin_chat_message(u.effective_chat.id, u.message.reply_to_message.message_id)
    msg = await u.message.reply_text('📌 已置顶')
    c.job_queue.run_once(lambda ctx: ctx.bot.delete_message(u.effective_chat.id, msg.message_id), 180)

async def cmd_unpin(u, c):
    if not await check_admin(u, c): return
    await c.bot.unpin_chat_message(u.effective_chat.id)
    msg = await u.message.reply_text('📌 已取消置顶')
    c.job_queue.run_once(lambda ctx: ctx.bot.delete_message(u.effective_chat.id, msg.message_id), 180)

async def cmd_purge(u, c):
    if not await check_admin(u, c): return await u.message.reply_text('❌ 无权限')
    try:
        n = min(int(c.args[0]), 100) if c.args else 10
    except (ValueError, IndexError):
        n = 10
    d = 0
    for i in range(n):
        try: await c.bot.delete_message(u.effective_chat.id, u.message.message_id - i - 1); d += 1
        except: pass
    try: await u.message.delete()
    except: pass
    m = await c.bot.send_message(u.effective_chat.id, f'🗑️ 删除 {d} 条')
    await asyncio.sleep(3)
    try: await m.delete()
    except: pass

async def new_member(u, c):
    s = db.get_settings(u.effective_chat.id)
    for m in u.message.new_chat_members:
        if m.is_bot: continue
        info = f'{m.first_name} (@{m.username})' if m.username else m.first_name
        blacklisted = db.is_blacklisted(m.id)
        if blacklisted:
            try:
                await c.bot.ban_chat_member(u.effective_chat.id, m.id)
                reason = blacklisted.get('reason', '未知')
                msg = await u.message.reply_text(f'🚫 {m.first_name} 在全局黑名单中\n原因: {reason}\n已被自动拒绝')
                c.job_queue.run_once(lambda ctx: ctx.bot.delete_message(u.effective_chat.id, msg.message_id), 10)
                await log_action(c, u.effective_chat.id, '🚫 黑名单拒绝', m, f'原因: {reason}')
            except Exception as e:
                logger.warning(f'Blacklist ban failed: {e}')
            continue
        await log_action(c, u.effective_chat.id, f'入群: {info}', m)
        # 进群立刻禁言，防止发广告
        try:
            await c.bot.restrict_chat_member(u.effective_chat.id, m.id, MUTED_PERMISSIONS)
        except Exception as e:
            logger.warning(f'restrict new member failed: {e}')
        if not s.get('welcome_enabled'): continue
        if s.get('verify_enabled'):
            captcha_text = generate_captcha(4)
            db.add_pending(m.id, u.effective_chat.id, captcha_text, time.time() + config.VERIFY_TIMEOUT)
            img_buffer = create_captcha_image(captcha_text)
            kb = build_captcha_buttons(captcha_text, m.id)
            caption = f'👋 欢迎 {m.first_name} 加入群组！\n\n🔐 请在 {config.VERIFY_TIMEOUT} 秒内点击验证码图片中的正确文字\n\n⚠️ 点错 3 次将被移出群组\n🚫 验证前已禁止发言'
            try:
                await u.message.reply_photo(photo=img_buffer, caption=caption, reply_markup=kb)
            except Exception as e:
                logger.warning(f'reply_photo failed: {e}')
            c.job_queue.run_once(verify_timeout, config.VERIFY_TIMEOUT, data={'uid': m.id, 'cid': u.effective_chat.id})
        else:
            # 没开验证也要解除禁言
            await c.bot.restrict_chat_member(u.effective_chat.id, m.id, FULL_PERMISSIONS)
            await u.message.reply_text(config.WELCOME_MSG.format(name=m.first_name, timeout=config.VERIFY_TIMEOUT))

async def verify_callback(u, c):
    q = u.callback_query
    data = q.data.split(':')
    action = data[0]
    target_id = int(data[1])

    # 管理员操作：清除警告 / 封禁用户
    if action in ('admin_unwarn', 'admin_ban'):
        if not await check_admin(u, c):
            await q.answer('❌ 无权限', show_alert=True)
            return
        cid = int(data[2])
        if action == 'admin_unwarn':
            db.reset_warns(target_id, cid)
            db.reset_spam_hits(target_id, cid)
            await q.answer('✅ 已清除警告')
            await q.edit_message_reply_markup(reply_markup=None)
            try:
                user = await c.bot.get_chat(target_id)
                uname = user.first_name
            except:
                uname = str(target_id)
            uobj = type('U', (), {'id': target_id, 'first_name': uname})()
            await log_action(c, cid, '✅ 清除警告', uobj, '管理员手动清除')
        elif action == 'admin_ban':
            try:
                await c.bot.ban_chat_member(cid, target_id)
                db.reset_warns(target_id, cid)
                db.reset_spam_hits(target_id, cid)
                await q.answer('🚫 已封禁')
                await q.edit_message_reply_markup(reply_markup=None)
                try:
                    user = await c.bot.get_chat(target_id)
                    uname = user.first_name
                except:
                    uname = str(target_id)
                uobj = type('U', (), {'id': target_id, 'first_name': uname})()
                await log_action(c, cid, '🚫 管理员封禁', uobj, '从通知按钮封禁')
            except Exception as e:
                await q.answer(f'❌ 操作失败: {e}', show_alert=True)
        return

    if action == 'unban_user':
        if not await check_admin(u, c):
            await q.answer('❌ 无权限', show_alert=True)
            return
        cid = int(data[2])
        try:
            await c.bot.unban_chat_member(cid, target_id)
            await q.answer('✅ 已解除封禁')
            await q.edit_message_reply_markup(reply_markup=None)
            await log_action(c, cid, '🔓 解除封禁', u.effective_user, f'用户 {target_id}')
        except Exception as e:
            await q.answer(f'❌ 操作失败: {e}', show_alert=True)
        return

    if action == 'report_user':
        if not await check_admin(u, c):
            await q.answer('❌ 无权限', show_alert=True)
            return
        cid = int(data[2])
        db.add_to_blacklist(target_id, '被举报骚扰', cid)
        await q.answer('✅ 已加入全局黑名单')
        await q.edit_message_reply_markup(reply_markup=None)
        try:
            user = await c.bot.get_chat(target_id)
            user_name = user.first_name
        except:
            user_name = str(target_id)
        user = type('U', (), {'id': target_id, 'first_name': user_name})()
        await log_action(c, cid, '🚫 举报骚扰', u.effective_user, f'用户 {target_id} 已加入全局黑名单')
        return

    if q.from_user.id != target_id:
        await q.answer('❌ 这不是你的验证', show_alert=True)
        return

    pending = db.get_pending(target_id, q.message.chat.id)
    if not pending:
        await q.answer('❌ 验证已过期', show_alert=True)
        return

    if action == 'verify_ok':
        await q.answer()
        db.remove_pending(target_id, q.message.chat.id)
        try:
            await c.bot.restrict_chat_member(q.message.chat.id, target_id, FULL_PERMISSIONS)
        except Exception as e:
            logger.warning(f'restrict_chat_member failed: {e}')
        await q.edit_message_caption(caption='✅ ' + q.from_user.first_name + ' 验证通过！欢迎加入群组！')
        await log_action(c, q.message.chat.id, '✅ 验证通过', q.from_user)
        await asyncio.sleep(3)
        try:
            await q.message.delete()
            logger.info(f'Deleted verify message for user {target_id}')
        except Exception as e:
            logger.warning(f'Delete verify message failed: {e}')
    elif action == 'verify_fail':
        await q.answer()
        fail_count = db.increment_verify_fail(target_id, q.message.chat.id)
        if fail_count >= 3:
            db.remove_pending(target_id, q.message.chat.id)
            await c.bot.ban_chat_member(q.message.chat.id, target_id)
            await q.edit_message_caption(caption=f'❌ {q.from_user.first_name} 验证失败超过3次，已被移出群组')
            await log_action(c, q.message.chat.id, '❌ 验证失败踢出', q.from_user, '答错3次')
            await asyncio.sleep(5)
            try:
                await q.message.delete()
                logger.info(f'Deleted verify fail message for user {target_id}')
            except Exception as e:
                logger.warning(f'Delete verify fail message failed: {e}')
        else:
            await q.answer(f'❌ 答案错误！还可尝试 {3 - fail_count} 次', show_alert=True)
    elif action == 'verify_refresh':
        refresh_count = db.increment_verify_refresh(target_id, q.message.chat.id)
        if refresh_count >= 3:
            await q.answer('❌ 已达到最大刷新次数', show_alert=True)
            return
        await q.answer()
        captcha_text = generate_captcha(4)
        db.add_pending(target_id, q.message.chat.id, captcha_text, time.time() + config.VERIFY_TIMEOUT)
        img_buffer = create_captcha_image(captcha_text)
        kb = build_captcha_buttons(captcha_text, target_id, refresh_count)
        caption = f'👋 欢迎 {q.from_user.first_name} 加入群组！\n\n🔐 请在 {config.VERIFY_TIMEOUT} 秒内点击验证码图片中的正确文字\n\n⚠️ 点错 3 次将被移出群组'
        await q.edit_message_media(
            media=InputMediaPhoto(media=img_buffer, caption=caption),
            reply_markup=kb
        )

async def verify_timeout(c):
    d = c.job.data
    if db.get_pending(d['uid'], d['cid']):
        await c.bot.ban_chat_member(d['cid'], d['uid'])
        db.remove_pending(d['uid'], d['cid'])
        try:
            user = await c.bot.get_chat(d['uid'])
            user_name = user.first_name
        except:
            user_name = str(d['uid'])
        user = type('U', (), {'id': d['uid'], 'first_name': user_name})()
        kb = InlineKeyboardMarkup([
            [InlineKeyboardButton('🔓 解除封禁', callback_data=f'unban_user:{d["uid"]}:{d["cid"]}')],
            [InlineKeyboardButton('🚫 举报并拒绝骚扰', callback_data=f'report_user:{d["uid"]}:{d["cid"]}')]
        ])
        msg = await c.bot.send_message(d['cid'], f'❌ `{user_name}` 验证超时，已被移出群组', parse_mode=ParseMode.MARKDOWN, reply_markup=kb)
        await log_action(c, d['cid'], '❌ 验证超时踢出', user, '超时未验证')
        c.job_queue.run_once(lambda ctx: ctx.bot.delete_message(d['cid'], msg.message_id), 60)

async def check_spam(u, c):
    try:
        if not u.message or u.effective_chat.type not in ['group', 'supergroup']: return
        if await check_admin(u, c): return
    except: return
    s = db.get_settings(u.effective_chat.id)
    if not s.get('antispam_enabled'): return
    r = check_message(u.message)
    if not r: return
    level, words = r
    logger.info(f'SPAM: user={u.effective_user.id} chat={u.effective_chat.id} level={level} words={words[:3]}')
    try: await u.message.delete()
    except: pass
    word_str = ', '.join(words[:3])
    if level == 'critical':
        await c.bot.ban_chat_member(u.effective_chat.id, u.effective_user.id)
        db.add_to_blacklist(u.effective_user.id, f'发送严重违规内容: {word_str}', u.effective_chat.id)
        m = await c.bot.send_message(u.effective_chat.id, f'🚫 {u.effective_user.first_name} 发送严重违规内容\n命中: {word_str}\n已封禁并加入全局黑名单')
        await log_action(c, u.effective_chat.id, '🚫 广告封禁', u.effective_user, f'命中: {word_str}')
        c.job_queue.run_once(lambda ctx: ctx.bot.delete_message(u.effective_chat.id, m.message_id), 10)
    else:
        # 累计命中次数，2 次才正式警告
        hit_count = db.add_spam_hit(u.effective_user.id, u.effective_chat.id)
        if hit_count < 2:
            # 第一次命中：静默删除 + 通知管理员
            await log_action(c, u.effective_chat.id, '⚠️ 广告警告', u.effective_user, f'命中: {word_str} ({hit_count}/2 待确认)')
            m = await c.bot.send_message(u.effective_chat.id, f'⚠️ {u.effective_user.first_name} 疑似违规\n命中: {word_str}\n消息已删除，请注意发言')
            c.job_queue.run_once(lambda ctx: ctx.bot.delete_message(u.effective_chat.id, m.message_id), 5)
        else:
            # 第二次命中：正式警告 + 重置计数
            db.reset_spam_hits(u.effective_user.id, u.effective_chat.id)
            n = db.add_warn(u.effective_user.id, u.effective_chat.id)
            txt = f'⚠️ {u.effective_user.first_name} 违规内容\n命中: {word_str}\n警告: {n}/{config.MAX_WARNS}'
            if n >= config.MAX_WARNS:
                await c.bot.ban_chat_member(u.effective_chat.id, u.effective_user.id)
                db.reset_warns(u.effective_user.id, u.effective_chat.id)
                txt += '\n🚫 累计警告达上限，已封禁'
                await log_action(c, u.effective_chat.id, '🚫 累计警告封禁', u.effective_user, f'命中: {word_str}')
            else:
                await log_action(c, u.effective_chat.id, '⚠️ 广告警告', u.effective_user, f'命中: {word_str} ({n}/{config.MAX_WARNS})')
            m = await c.bot.send_message(u.effective_chat.id, txt)
            c.job_queue.run_once(lambda ctx: ctx.bot.delete_message(u.effective_chat.id, m.message_id), 5)

async def cmd_settings(u, c):
    s = db.get_settings(u.effective_chat.id)
    txt = '⚙️ 设置\n欢迎: ' + ('✅' if s.get('welcome_enabled') else '❌') + '\n验证: ' + ('✅' if s.get('verify_enabled') else '❌') + '\n反垃圾: ' + ('✅' if s.get('antispam_enabled') else '❌') + '\n最大警告: ' + str(config.MAX_WARNS)
    msg = await u.message.reply_text(txt, parse_mode=ParseMode.MARKDOWN)
    c.job_queue.run_once(lambda ctx: ctx.bot.delete_message(u.effective_chat.id, msg.message_id), 180)

async def cmd_blacklist(u, c):
    if not await check_admin(u, c): return
    keyword = c.args[0] if c.args else None
    if keyword:
        users = db.search_blacklist(keyword)
    else:
        users = db.get_blacklist(20)
    if not users:
        msg = await u.message.reply_text('📋 黑名单为空')
        c.job_queue.run_once(lambda ctx: ctx.bot.delete_message(u.effective_chat.id, msg.message_id), 30)
        return
    lines = ['📋 **全局黑名单**\n']
    cst = timezone(timedelta(hours=8))
    for user in users:
        t = datetime.fromtimestamp(user['added_at'], cst).strftime('%m-%d %H:%M')
        lines.append(f'`{user["user_id"]}` - {user["reason"][:20]} ({t})')
    text = '\n'.join(lines)
    if len(text) > 4000:
        text = text[:4000] + '\n...'
    msg = await u.message.reply_text(text, parse_mode=ParseMode.MARKDOWN)
    c.job_queue.run_once(lambda ctx: ctx.bot.delete_message(u.effective_chat.id, msg.message_id), 60)

async def cmd_userinfo(u, c):
    if not await check_admin(u, c): return
    target = get_target(u, c)
    if not target:
        try: target = int(c.args[0]) if c.args else None
        except: pass
    if not target: return await u.message.reply_text('❌ 指定用户ID')
    info = db.get_user_info(target)
    lines = [f'👤 **用户信息** `{target}`\n']
    if info['blacklisted']:
        lines.append(f'🚫 **全局黑名单**: {info["blacklisted"]["reason"]}')
    if info['warnings']:
        for w in info['warnings']:
            lines.append(f'⚠️ 群 `{w["chat_id"]}` 警告: {w["count"]}')
    if info['muted']:
        for m in info['muted']:
            lines.append(f'🔇 群 `{m["chat_id"]}` 禁言')
    if info['pending_verify']:
        for p in info['pending_verify']:
            lines.append(f'🔐 群 `{p["chat_id"]}` 待验证')
    if len(lines) == 1:
        lines.append('✅ 无记录')
    msg = await u.message.reply_text('\n'.join(lines), parse_mode=ParseMode.MARKDOWN)
    c.job_queue.run_once(lambda ctx: ctx.bot.delete_message(u.effective_chat.id, msg.message_id), 60)

async def toggle(u, c, k):
    if not await check_admin(u, c): return
    s = db.get_settings(u.effective_chat.id)
    v = 0 if s.get(k) else 1
    db.update_setting(u.effective_chat.id, k, v)
    msg_text = '✅ ' + ('开启' if v else '关闭')
    # 开关验证时自动设置群默认权限
    if k == 'verify_enabled':
        try:
            if v:
                await c.bot.set_chat_permissions(u.effective_chat.id, MUTED_PERMISSIONS)
                msg_text += '\n🔒 群默认权限已设为禁言（新人进群自动禁言）'
            else:
                await c.bot.set_chat_permissions(u.effective_chat.id, FULL_PERMISSIONS)
                msg_text += '\n🔓 群默认权限已恢复（新人可发言）'
        except Exception as e:
            msg_text += f'\n⚠️ 设置群权限失败: {e}'
            logger.warning(f'set_chat_permissions failed: {e}')
    msg = await u.message.reply_text(msg_text)
    c.job_queue.run_once(lambda ctx: ctx.bot.delete_message(u.effective_chat.id, msg.message_id), 180)

async def cmd_lock(u, c):
    """锁定群：新成员默认禁言"""
    if not await check_admin(u, c): return
    try:
        await c.bot.set_chat_permissions(u.effective_chat.id, MUTED_PERMISSIONS)
        msg = await u.message.reply_text('🔒 已锁定群聊\n新成员进群默认禁言，需管理员解除')
        c.job_queue.run_once(lambda ctx: ctx.bot.delete_message(u.effective_chat.id, msg.message_id), 180)
    except Exception as e:
        await u.message.reply_text(f'❌ 操作失败: {e}')

async def cmd_unlock(u, c):
    """解锁群：恢复默认发言权限"""
    if not await check_admin(u, c): return
    try:
        await c.bot.set_chat_permissions(u.effective_chat.id, FULL_PERMISSIONS)
        msg = await u.message.reply_text('🔓 已解锁群聊\n新成员进群可正常发言')
        c.job_queue.run_once(lambda ctx: ctx.bot.delete_message(u.effective_chat.id, msg.message_id), 180)
    except Exception as e:
        await u.message.reply_text(f'❌ 操作失败: {e}')

def main():
    global db
    db = Database(config.DB_PATH)

    proxy_url = config.PROXY
    builder = Application.builder().token(config.BOT_TOKEN)
    if proxy_url:
        builder = builder.proxy(proxy_url)
        builder = builder.get_updates_proxy(proxy_url)

    builder = builder.connect_timeout(30)
    builder = builder.read_timeout(30)

    app = builder.post_init(post_init).build()
    for cmd, f in [('start', cmd_start), ('help', cmd_help), ('ban', cmd_ban), ('unban', cmd_unban),
                   ('kick', cmd_kick), ('mute', cmd_mute), ('unmute', cmd_unmute), ('warn', cmd_warn),
                   ('unwarn', cmd_unwarn), ('warns', cmd_warns), ('pin', cmd_pin), ('unpin', cmd_unpin),
                   ('purge', cmd_purge), ('settings', cmd_settings),
                   ('welcome', lambda u, c: toggle(u, c, 'welcome_enabled')),
                   ('verify', lambda u, c: toggle(u, c, 'verify_enabled')),
                   ('lock', cmd_lock), ('unlock', cmd_unlock),
                   ('antispam', lambda u, c: toggle(u, c, 'antispam_enabled')),
                   ('blacklist', cmd_blacklist), ('userinfo', cmd_userinfo)]:
        app.add_handler(CommandHandler(cmd, f))

    async def on_my_chat_member(u, c):
        chat = u.effective_chat
        logger.info(f'MY_CHAT_MEMBER: chat_id={chat.id} title={chat.title} type={chat.type}')

    async def on_join_request(u, c):
        user = u.from_user
        chat = u.chat
        info = f"{user.first_name} (@{user.username})" if user.username else user.first_name
        logger.info(f'JOIN_REQUEST: {chat.id} {chat.title} {info}')
        await log_action(c, chat.id, f'入群申请: {info}', user)
        try:
            await c.bot.send_message(config.LOG_CHAT_ID, f'入群申请 群组: {chat.title} 用户: {info} ID: {user.id}', parse_mode=None)
        except: pass

    app.add_handler(ChatMemberHandler(on_my_chat_member, ChatMemberHandler.MY_CHAT_MEMBER))
    app.add_handler(ChatJoinRequestHandler(on_join_request))
    app.add_handler(MessageHandler(filters.StatusUpdate.NEW_CHAT_MEMBERS, new_member))
    app.add_handler(CallbackQueryHandler(verify_callback, pattern=r'^(verify_|admin_|unban_|report_)'))
    app.add_handler(MessageHandler(filters.ALL & ~filters.COMMAND & filters.ChatType.GROUPS, check_spam))

    app.run_polling()

if __name__ == '__main__':
    main()

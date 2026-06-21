import os
import time
import random
import logging
import asyncio
from datetime import datetime
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ChatPermissions
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, ContextTypes, filters
from telegram.constants import ChatMemberStatus, ParseMode
from telegram import InputMediaPhoto
import config
from database import Database
from filters import check_message
from captcha import generate_captcha, create_captcha_image, generate_fake_options

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
    t = f'📋 **{action}**\n群组: `{cid}`\n'
    if user: t += f'操作者: {user.first_name} (`{user.id}`)\n'
    if reason: t += f'原因: {reason}\n'
    t += f'时间: {datetime.now().strftime("%H:%M:%S")}'
    try: await context.bot.send_message(config.LOG_CHAT_ID, t, parse_mode=ParseMode.MARKDOWN)
    except: pass

def parse_time(s):
    if not s: return None
    s = s.lower()
    if s.endswith('m'): return int(s[:-1]) * 60
    if s.endswith('h'): return int(s[:-1]) * 3600
    if s.endswith('d'): return int(s[:-1]) * 86400
    return int(s) * 60

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

async def cmd_start(u, c): await u.message.reply_text('🤖 群管机器人\n/help 查看命令')
async def cmd_help(u, c): await u.message.reply_text('/ban /unban /kick /mute /unmute /warn /unwarn /warns /pin /unpin /purge\n/welcome /verify /antispam /settings', parse_mode=ParseMode.MARKDOWN)

async def cmd_ban(u, c):
    if not await check_admin(u, c): return await u.message.reply_text('❌ 无权限')
    t = get_target(u, c)
    if not t: return await u.message.reply_text('❌ 指定用户')
    r = ' '.join(c.args[1:]) if len(c.args) > 1 else '无'
    await c.bot.ban_chat_member(u.effective_chat.id, t)
    await u.message.reply_text(f'✅ 封禁 `{t}`\n原因: {r}', parse_mode=ParseMode.MARKDOWN)
    await log_action(c, u.effective_chat.id, '封禁', u.effective_user, r)

async def cmd_unban(u, c):
    if not await check_admin(u, c): return await u.message.reply_text('❌ 无权限')
    t = get_target(u, c)
    if not t: return await u.message.reply_text('❌ 指定用户')
    await c.bot.unban_chat_member(u.effective_chat.id, t)
    await u.message.reply_text(f'✅ 解封 `{t}`', parse_mode=ParseMode.MARKDOWN)

async def cmd_kick(u, c):
    if not await check_admin(u, c): return await u.message.reply_text('❌ 无权限')
    t = get_target(u, c)
    if not t: return await u.message.reply_text('❌ 指定用户')
    await c.bot.ban_chat_member(u.effective_chat.id, t)
    await asyncio.sleep(1)
    await c.bot.unban_chat_member(u.effective_chat.id, t)
    await u.message.reply_text(f'✅ 踢出 `{t}`', parse_mode=ParseMode.MARKDOWN)

async def cmd_mute(u, c):
    if not await check_admin(u, c): return await u.message.reply_text('❌ 无权限')
    t, ts = get_target_time(u, c)
    if not t: return await u.message.reply_text('❌ 指定用户')
    d = parse_time(ts)
    un = int(time.time() + d) if d else None
    await c.bot.restrict_chat_member(u.effective_chat.id, t, ChatPermissions(can_send_messages=False), until_date=un)
    db.add_mute(t, u.effective_chat.id, time.time() + d if d else 0)
    await u.message.reply_text(f'🔇 禁言 `{t}` {ts or "永久"}', parse_mode=ParseMode.MARKDOWN)

async def cmd_unmute(u, c):
    if not await check_admin(u, c): return await u.message.reply_text('❌ 无权限')
    t = get_target(u, c)
    if not t: return await u.message.reply_text('❌ 指定用户')
    p = ChatPermissions(can_send_messages=True, can_send_media_messages=True, can_send_other_messages=True, can_add_web_page_previews=True)
    await c.bot.restrict_chat_member(u.effective_chat.id, t, p)
    db.remove_mute(t, u.effective_chat.id)
    await u.message.reply_text(f'🔊 解禁 `{t}`', parse_mode=ParseMode.MARKDOWN)

async def cmd_warn(u, c):
    if not await check_admin(u, c): return await u.message.reply_text('❌ 无权限')
    t = get_target(u, c)
    if not t: return await u.message.reply_text('❌ 指定用户')
    r = ' '.join(c.args[1:]) if len(c.args) > 1 else '无'
    n = db.add_warn(t, u.effective_chat.id)
    txt = f'⚠️ `{t}` 警告 ({n}/{config.MAX_WARNS})\n原因: {r}'
    if n >= config.MAX_WARNS:
        await c.bot.ban_chat_member(u.effective_chat.id, t)
        db.reset_warns(t, u.effective_chat.id)
        txt += '\n🚫 已封禁'
    await u.message.reply_text(txt, parse_mode=ParseMode.MARKDOWN)
    await log_action(c, u.effective_chat.id, '警告', u.effective_user, f'{r} ({n})')

async def cmd_unwarn(u, c):
    if not await check_admin(u, c): return await u.message.reply_text('❌ 无权限')
    t = get_target(u, c)
    if not t: return await u.message.reply_text('❌ 指定用户')
    db.reset_warns(t, u.effective_chat.id)
    await u.message.reply_text(f'✅ 已清除 `{t}` 警告', parse_mode=ParseMode.MARKDOWN)

async def cmd_warns(u, c):
    t = get_target(u, c) or u.effective_user.id
    n = db.get_warns(t, u.effective_chat.id)
    await u.message.reply_text(f'⚠️ `{t}` 警告: {n}/{config.MAX_WARNS}', parse_mode=ParseMode.MARKDOWN)

async def cmd_pin(u, c):
    if not await check_admin(u, c): return await u.message.reply_text('❌ 无权限')
    if not u.message.reply_to_message: return await u.message.reply_text('❌ 回复消息')
    await c.bot.pin_chat_message(u.effective_chat.id, u.message.reply_to_message.message_id)
    await u.message.reply_text('📌 已置顶')

async def cmd_unpin(u, c):
    if not await check_admin(u, c): return await u.message.reply_text('❌ 无权限')
    await c.bot.unpin_chat_message(u.effective_chat.id)
    await u.message.reply_text('📌 已取消置顶')

async def cmd_purge(u, c):
    if not await check_admin(u, c): return await u.message.reply_text('❌ 无权限')
    n = min(int(c.args[0]) if c.args else 10, 100)
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
        if m.is_bot or not s.get('welcome_enabled'): continue
        if s.get('verify_enabled'):
            # 生成验证码
            captcha_text = generate_captcha(4)
            db.add_pending(m.id, u.effective_chat.id, captcha_text, time.time() + config.VERIFY_TIMEOUT)
            
            # 生成验证码图片
            img_buffer = create_captcha_image(captcha_text)
            
            # 生成选项按钮
            options = generate_fake_options(captcha_text, 5)
            buttons = []
            row = []
            for opt in options:
                if opt == captcha_text:
                    row.append(InlineKeyboardButton(opt, callback_data='verify_ok:' + str(m.id)))
                else:
                    row.append(InlineKeyboardButton(opt, callback_data='verify_fail:' + str(m.id)))
                if len(row) == 3:
                    buttons.append(row)
                    row = []
            if row:
                buttons.append(row)
            buttons.append([InlineKeyboardButton('🔄 换一张', callback_data='verify_refresh:' + str(m.id))])
            kb = InlineKeyboardMarkup(buttons)
            
            caption = '👋 欢迎 ' + m.first_name + ' 加入群组！\n\n🔐 请在 ' + str(config.VERIFY_TIMEOUT) + ' 秒内点击验证码图片中的正确文字\n\n⚠️ 点错 3 次将被移出群组\n🚫 验证前禁止发言'
            await u.message.reply_photo(photo=img_buffer, caption=caption, reply_markup=kb)
            
            # 禁言直到验证通过
            await c.bot.restrict_chat_member(u.effective_chat.id, m.id, ChatPermissions(can_send_messages=False))
            
            c.job_queue.run_once(verify_timeout, config.VERIFY_TIMEOUT, data={'uid': m.id, 'cid': u.effective_chat.id})
        else:
            await u.message.reply_text(config.WELCOME_MSG.format(name=m.first_name, timeout=config.VERIFY_TIMEOUT))

async def verify_timeout(c):
    d = c.job.data
    if db.get_pending(d['uid'], d['cid']):
        await c.bot.ban_chat_member(d['cid'], d['uid'])
        await c.bot.send_message(d['cid'], f'❌ `{d["uid"]}` 超时', parse_mode=ParseMode.MARKDOWN)
        db.remove_pending(d['uid'], d['cid'])

async def verify_callback(u, c):
    """处理验证码按钮回调"""
    q = u.callback_query
    await q.answer()
    
    data = q.data.split(':')
    action = data[0]
    target_id = int(data[1])
    
    # 检查是否是本人操作
    if q.from_user.id != target_id:
        await q.answer('❌ 这不是你的验证', show_alert=True)
        return
    
    pending = db.get_pending(target_id, q.message.chat.id)
    if not pending:
        await q.answer('❌ 验证已过期', show_alert=True)
        return
    
    if action == 'verify_ok':
        # 验证成功
        db.remove_pending(target_id, q.message.chat.id)
        
        # 解除禁言
        permissions = ChatPermissions(can_send_messages=True, can_send_media_messages=True, can_send_other_messages=True, can_add_web_page_previews=True)
        await c.bot.restrict_chat_member(q.message.chat.id, target_id, permissions)
        
        await q.edit_message_caption(caption='✅ ' + q.from_user.first_name + ' 验证通过！欢迎加入群组！')
        
        # 3秒后删除验证码消息
        await asyncio.sleep(3)
        try:
            await q.message.delete()
        except:
            pass
    elif action == 'verify_fail':
        # 验证失败
        fail_count = db.increment_verify_fail(target_id, q.message.chat.id)
        if fail_count >= 3:
            # 超过3次，踢出
            db.remove_pending(target_id, q.message.chat.id)
            await c.bot.ban_chat_member(q.message.chat.id, target_id)
            await q.edit_message_caption(caption=f'❌ {q.from_user.first_name} 验证失败超过3次，已被移出群组')
        else:
            await q.answer(f'❌ 答案错误！还可尝试 {3 - fail_count} 次', show_alert=True)
    elif action == 'verify_refresh':
        # 刷新验证码
        refresh_count = db.increment_verify_refresh(target_id, q.message.chat.id)
        if refresh_count >= 3:
            await q.answer('❌ 已达到最大刷新次数', show_alert=True)
            return
        
        # 生成新验证码
        captcha_text = generate_captcha(4)
        db.add_pending(target_id, q.message.chat.id, captcha_text, time.time() + config.VERIFY_TIMEOUT)
        
        # 生成新图片和按钮
        img_buffer = create_captcha_image(captcha_text)
        options = generate_fake_options(captcha_text, 5)
        buttons = []
        row = []
        for opt in options:
            if opt == captcha_text:
                row.append(InlineKeyboardButton(opt, callback_data='verify_ok:' + str(target_id)))
            else:
                row.append(InlineKeyboardButton(opt, callback_data='verify_fail:' + str(target_id)))
            if len(row) == 3:
                buttons.append(row)
                row = []
        if row:
            buttons.append(row)
        buttons.append([InlineKeyboardButton('🔄 换一张 (' + str(3 - refresh_count) + ')', callback_data='verify_refresh:' + str(target_id))])
        kb = InlineKeyboardMarkup(buttons)
        
        caption = '👋 欢迎 ' + q.from_user.first_name + ' 加入群组！\n\n🔐 请在 ' + str(config.VERIFY_TIMEOUT) + ' 秒内点击验证码图片中的正确文字\n\n⚠️ 点错 3 次将被移出群组'
        await q.edit_message_media(
            media=InputMediaPhoto(media=img_buffer, caption=caption),
            reply_markup=kb
        )

async def verify_timeout(c):
    d = c.job.data
    if db.get_pending(d['uid'], d['cid']):
        await c.bot.ban_chat_member(d['cid'], d['uid'])
        await c.bot.send_message(d['cid'], f'❌ `{d["uid"]}` 验证超时，已被移出群组', parse_mode=ParseMode.MARKDOWN)
        db.remove_pending(d['uid'], d['cid'])

async def check_spam(u, c):
    if not u.message or u.effective_chat.type not in ['group', 'supergroup']: return
    if await check_admin(u, c): return
    s = db.get_settings(u.effective_chat.id)
    if not s.get('antispam_enabled'): return
    r = check_message(u.message)
    if not r: return
    try: await u.message.delete()
    except: pass
    
    level, words = r
    word_str = ', '.join(words[:3])
    
    if level == 'critical':
        # 严重违规 - 直接封禁
        await c.bot.ban_chat_member(u.effective_chat.id, u.effective_user.id)
        txt = f'🚫 {u.effective_user.first_name} 发送严重违规内容\n命中: {word_str}\n已封禁'
        m = await c.bot.send_message(u.effective_chat.id, txt)
        await asyncio.sleep(10)
        try: await m.delete()
        except: pass
    else:
        # 一般违规 - 警告
        n = db.add_warn(u.effective_user.id, u.effective_chat.id)
        txt = f'⚠️ {u.effective_user.first_name} 违规内容\n命中: {word_str}\n警告: {n}/{config.MAX_WARNS}'
        if n >= config.MAX_WARNS:
            await c.bot.ban_chat_member(u.effective_chat.id, u.effective_user.id)
            db.reset_warns(u.effective_user.id, u.effective_chat.id)
            txt += '\n🚫 累计警告达上限，已封禁'
        m = await c.bot.send_message(u.effective_chat.id, txt)
        await asyncio.sleep(5)
        try: await m.delete()
        except: pass

async def cmd_settings(u, c):
    s = db.get_settings(u.effective_chat.id)
    await u.message.reply_text(f'⚙️ 设置\n欢迎: {"✅" if s.get("welcome_enabled") else "❌"}\n验证: {"✅" if s.get("verify_enabled") else "❌"}\n反垃圾: {"✅" if s.get("antispam_enabled") else "❌"}\n最大警告: {config.MAX_WARNS}', parse_mode=ParseMode.MARKDOWN)

async def toggle(u, c, k):
    if not await check_admin(u, c): return await u.message.reply_text('❌ 无权限')
    s = db.get_settings(u.effective_chat.id)
    v = 0 if s.get(k) else 1
    db.update_setting(u.effective_chat.id, k, v)
    await u.message.reply_text(f'✅ {"开启" if v else "关闭"}')

def main():
    global db
    db = Database(config.DB_PATH)
    
    # 代理配置
    proxy_url = os.environ.get('HTTP_PROXY') or os.environ.get('HTTPS_PROXY')
    builder = Application.builder().token(config.BOT_TOKEN)
    if proxy_url:
        builder = builder.proxy(proxy_url)
        builder = builder.get_updates_proxy(proxy_url)
    
    # 增加超时时间
    builder = builder.connect_timeout(30)
    builder = builder.read_timeout(30)
    
    app = builder.build()
    for cmd, f in [('start', cmd_start), ('help', cmd_help), ('ban', cmd_ban), ('unban', cmd_unban),
                   ('kick', cmd_kick), ('mute', cmd_mute), ('unmute', cmd_unmute), ('warn', cmd_warn),
                   ('unwarn', cmd_unwarn), ('warns', cmd_warns), ('pin', cmd_pin), ('unpin', cmd_unpin),
                   ('purge', cmd_purge), ('settings', cmd_settings),
                   ('welcome', lambda u, c: toggle(u, c, 'welcome_enabled')),
                   ('verify', lambda u, c: toggle(u, c, 'verify_enabled')),
                   ('antispam', lambda u, c: toggle(u, c, 'antispam_enabled'))]:
        app.add_handler(CommandHandler(cmd, f))
    app.add_handler(MessageHandler(filters.StatusUpdate.NEW_CHAT_MEMBERS, new_member))
    app.add_handler(CallbackQueryHandler(verify_callback, pattern=r'^verify_'))
    app.add_handler(MessageHandler(filters.ALL & ~filters.COMMAND & filters.ChatType.GROUPS, check_spam))
    logger.info('Bot 启动中...')
    app.run_polling(drop_pending_updates=True)

if __name__ == '__main__':
    main()

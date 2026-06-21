import re
from config import BANNED_WORDS, BAN_LINKS, BAN_FORWARDS

URL_PATTERN = re.compile(
    r'https?://|www\.|t\.me/|telegram\.me/|telegram\.dog/|bit\.ly/|tinyurl\.com/'
)

# 零宽字符列表
ZERO_WIDTH_CHARS = re.compile(r'[​‌‍‎‏﻿  ‪-‮⁠-⁤⁪-⁯￹-￻­͏؜ᅟᅠ឴឵᠎ㅤﾠ]')

# 严重词库 - 直接封禁
CRITICAL_WORDS = [
    '博彩', '彩票', '赌', '开奖', '下注', '赔率', '赌场', '网赌', '外围',
    '百家乐', '老虎机', '轮盘', '德州扑克', '六合彩', '时时彩', '北京赛车',
    '约炮', '约p', '约P', '裸聊', '成人',
    '贷款', '借钱', '低息', '无抵押', '信用贷', '套现', '花呗', '借呗',
    '信用卡', 'POS机', '养卡',
    '代开', '办证', '发票',
]

# 一般词库 - 警告
WARNING_WORDS = [
    '刷单', '兼职', '日赚', '躺赚', '零投资', '高回报', '稳赚',
    '刷信誉', '刷好评', '日结', '在家赚钱', '手机赚钱', '副业', '薅羊毛',
    '加微信', '加v', '加V', '私聊', '私我', '优惠券', '返利', '返现',
    '免费领', '免费送', '限时', '秒杀', '清仓', '特价', '打折', '优惠',
    '代理', '招代理', '加盟', '分销', '推广', '引流', '变现',
    '代发', '代写', '代做', '代考',
    '群发', '自动加人', '脚本', '外挂', '破解', 'VPN', '翻墙',
    '手游', '充值', '折扣', '首充', '礼包', '代练',
    # 典型诈骗话术
    '风口', '机会', '轻松', '头相', '老表', '抓住', '五W', '5W',
    # 引流话术
    '远控', '实测', '免费测试', '支持测试', '可看', '可试',
    '私', '带', '教程', '资源', '分享', '打包',
    '项目', '赚钱项目', '引流', '变现', '躺赚',
    # 色情引流
    '福利', '资源群', '视频', '约', '上门',
    '服务', '全套', '楼凤',
]

def clean_text(text):
    """清除零宽字符和特殊字符"""
    text = ZERO_WIDTH_CHARS.sub('', text)
    text = text.lower().strip()
    return text

def check_message(message):
    """检查消息是否违规，返回 (类型, 关键词列表)"""
    raw_text = (message.text or message.caption or '')
    text = clean_text(raw_text)
    
    critical_hits = [w for w in CRITICAL_WORDS if w.lower() in text]
    warning_hits = [w for w in WARNING_WORDS if w.lower() in text]
    
    # 严重词命中任意一个 → 直接封禁
    if critical_hits:
        return ('critical', critical_hits)
    
    # 一般词命中 3 个以上 → 也封禁
    if len(warning_hits) >= 3:
        return ('critical', warning_hits)
    
    # 一般词命中 1-2 个 → 警告
    if warning_hits:
        return ('warning', warning_hits)
    
    # 链接
    if BAN_LINKS and URL_PATTERN.search(text):
        return ('warning', ['链接'])
    
    # 转发
    if BAN_FORWARDS and (message.forward_from or message.forward_from_chat):
        return ('warning', ['转发'])
    
    return None

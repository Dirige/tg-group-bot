import re
from config import BANNED_WORDS, BAN_LINKS, BAN_FORWARDS

URL_PATTERN = re.compile(
    r'https?://|www\.|t\.me/|telegram\.me/|telegram\.dog/|bit\.ly/|tinyurl\.com/'
)

ZERO_WIDTH_CHARS = re.compile(r'[\u200b\u200c\u200d\u200e\u200f\u202a-\u202e\u2060-\u2064\u2066-\u206f\ufeff\u2028\u2029\u2000-\u200a\u00ad\u061c\u180e\u2065\u2800\u3164\uffa0]')

CRITICAL_WORDS = [
    '博彩', '彩票', '赌', '开奖', '下注', '赔率', '赌场', '网赌', '外围',
    '百家乐', '老虎机', '轮盘', '德州扑克', '六合彩', '时时彩', '北京赛车',
    '约炮', '约p', '约P', '裸聊', '成人',
    '贷款', '借钱', '低息', '无抵押', '信用贷', '套现', '花呗', '借呗',
    '信用卡', 'POS机', '养卡',
    '代开', '办证', '发票',
]

WARNING_WORDS = [
    '刷单', '兼职', '日赚', '躺赚', '零投资', '高回报', '稳赚',
    '刷信誉', '刷好评', '日结', '在家赚钱', '手机赚钱', '副业', '薅羊毛',
    '加微信', '加v', '加V', '私聊', '私我', '优惠券', '返利', '返现',
    '免费领', '免费送', '限时', '秒杀', '清仓', '特价', '打折', '优惠',
    '代理', '招代理', '加盟', '分销', '推广', '引流', '变现',
    '代发', '代写', '代做', '代考',
    '群发', '自动加人', '脚本', '外挂', '破解', 'VPN', '翻墙',
    '手游', '充值', '折扣', '首充', '礼包', '代练',
    '风口', '机会', '轻松', '头相', '老表', '抓住', '五W', '5W',
    '远控', '实测', '免费测试', '支持测试', '可看', '可试',
    '私', '带', '教程', '资源', '分享', '打包',
    '项目', '赚钱项目',
    '福利', '资源群', '视频', '约', '上门',
    '服务', '全套', '楼凤',
    '保底', '偏门', '路子', '走偏', '偏们', '看我简', '看我主',
    '日入', '月入', '年入', '一天', 'w+', 'w看', 'W看',
    '稳赚不赔', '零风险', '保证赚', '包赚',
    '看简介', '看签名', '主页有', '头像有', '头相有',
    '扣我', '联系我', '加我', '找我',
    '做事', '五k', '5k', '多劳多得', '了解更多',
    '天上掉', '带你赚', '带你做', '小白可', '新手可',
    '动动手指', '手机操作', '日入过',
    '看片', '看剧', '免费看', 'vip',
    '简jie', '主ye', '头xiang',
]

def clean_text(text):
    text = ZERO_WIDTH_CHARS.sub('', text)
    text = text.lower().strip()
    text = re.sub(r'(?<=[一-鿿])\s+(?=[一-鿿])', '', text)
    text = re.sub(r'(?<=[一-鿿])\s+(?=[a-zA-Z0-9])', '', text)
    text = re.sub(r'(?<=[a-zA-Z0-9])\s+(?=[一-鿿])', '', text)
    return text

def count_zero_width(text):
    return len(ZERO_WIDTH_CHARS.findall(text))

def check_message(message):
    raw_text = (message.text or message.caption or '')
    text = clean_text(raw_text)

    zw_count = count_zero_width(raw_text)
    if zw_count >= 5 or (len(raw_text) > 0 and zw_count / len(raw_text) > 0.05):
        return ('critical', [f'零宽字符×{zw_count}'])

    custom_hits = [w for w in BANNED_WORDS if w.lower() in text]
    if custom_hits:
        return ('critical', custom_hits)

    critical_hits = [w for w in CRITICAL_WORDS if w.lower() in text]
    warning_hits = [w for w in WARNING_WORDS if w.lower() in text]

    if critical_hits:
        return ('critical', critical_hits)

    if len(warning_hits) >= 3:
        return ('critical', warning_hits)

    if warning_hits:
        return ('warning', warning_hits)

    if BAN_LINKS and URL_PATTERN.search(text):
        return ('warning', ['链接'])

    if BAN_FORWARDS and (message.forward_from or message.forward_from_chat):
        return ('warning', ['转发'])

    return None

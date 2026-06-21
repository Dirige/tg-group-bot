import random
import string
from io import BytesIO
from PIL import Image, ImageDraw, ImageFont

# 验证码字符集（去掉容易混淆的字符）
CHARS = 'ABCDEFGHJKLMNPQRSTUVWXYZ23456789'

def generate_captcha(length=4):
    """生成验证码文本"""
    return ''.join(random.choice(CHARS) for _ in range(length))

def create_captcha_image(text, width=200, height=80):
    """生成验证码图片"""
    # 创建图片
    img = Image.new('RGB', (width, height), color=(
        random.randint(200, 255),
        random.randint(200, 255),
        random.randint(200, 255)
    ))
    draw = ImageDraw.Draw(img)
    
    # 尝试加载字体，如果失败使用默认字体
    try:
        font = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf', 36)
    except:
        font = ImageFont.load_default()
    
    # 绘制干扰线
    for _ in range(5):
        x1 = random.randint(0, width)
        y1 = random.randint(0, height)
        x2 = random.randint(0, width)
        y2 = random.randint(0, height)
        color = (random.randint(0, 200), random.randint(0, 200), random.randint(0, 200))
        draw.line([(x1, y1), (x2, y2)], fill=color, width=2)
    
    # 绘制噪点
    for _ in range(100):
        x = random.randint(0, width)
        y = random.randint(0, height)
        color = (random.randint(0, 200), random.randint(0, 200), random.randint(0, 200))
        draw.point((x, y), fill=color)
    
    # 绘制验证码文字
    x_offset = 20
    for char in text:
        color = (random.randint(0, 100), random.randint(0, 100), random.randint(0, 100))
        y_offset = random.randint(5, 15)
        draw.text((x_offset, y_offset), char, fill=color, font=font)
        x_offset += 40 + random.randint(-5, 5)
    
    # 转为字节流
    buffer = BytesIO()
    img.save(buffer, format='PNG')
    buffer.seek(0)
    return buffer

def generate_fake_options(correct_answer, count=5):
    """生成假选项"""
    options = set()
    options.add(correct_answer)
    while len(options) < count + 1:
        fake = ''.join(random.choice(CHARS) for _ in range(len(correct_answer)))
        options.add(fake)
    options = list(options)
    random.shuffle(options)
    return options

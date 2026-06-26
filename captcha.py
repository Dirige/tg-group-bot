import random
from io import BytesIO
from PIL import Image, ImageDraw, ImageFont

CHARS = 'ABCDEFGHJKLMNPQRSTUVWXYZ23456789'

def generate_captcha(length=4):
    return ''.join(random.choice(CHARS) for _ in range(length))

def create_captcha_image(text, width=200, height=80):
    img = Image.new('RGB', (width, height), color=(
        random.randint(200, 255),
        random.randint(200, 255),
        random.randint(200, 255)
    ))
    draw = ImageDraw.Draw(img)

    try:
        font = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf', 36)
    except:
        font = ImageFont.load_default()

    for _ in range(5):
        x1, y1 = random.randint(0, width), random.randint(0, height)
        x2, y2 = random.randint(0, width), random.randint(0, height)
        draw.line([(x1, y1), (x2, y2)], fill=(random.randint(0, 200),) * 3, width=2)

    for _ in range(100):
        draw.point((random.randint(0, width), random.randint(0, height)),
                    fill=(random.randint(0, 200),) * 3)

    x_offset = 20
    for char in text:
        draw.text((x_offset, random.randint(5, 15)), char,
                  fill=(random.randint(0, 100),) * 3, font=font)
        x_offset += 40 + random.randint(-5, 5)

    buffer = BytesIO()
    img.save(buffer, format='PNG')
    buffer.seek(0)
    return buffer

def generate_fake_options(correct_answer, count=5):
    options = {correct_answer}
    while len(options) < count + 1:
        options.add(''.join(random.choice(CHARS) for _ in range(len(correct_answer))))
    result = list(options)
    random.shuffle(result)
    return result

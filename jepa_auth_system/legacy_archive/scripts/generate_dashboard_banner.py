from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

out = Path(__file__).resolve().parents[1] / 'assets' / 'dashboard_banner.png'
out.parent.mkdir(exist_ok=True)

img = Image.new('RGBA', (420, 140), (8, 15, 27, 255))
draw = ImageDraw.Draw(img)

for y in range(140):
    c = int(18 + (y / 140) * 40)
    draw.line((0, y, 420, y), fill=(20, 30, 45, c))

for x in range(0, 420, 40):
    draw.rectangle((x, 18, x + 30, 122), fill=(15, 118, 110, 200))
    draw.rectangle((x + 35, 30, x + 70, 110), fill=(56, 189, 248, 160))
    draw.rectangle((x + 75, 22, x + 110, 118), fill=(221, 119, 22, 180))

# main card

draw.rounded_rectangle((28, 24, 392, 116), radius=18, fill=(15, 23, 42, 220), outline=(30, 41, 59, 255), width=2)

try:
    font = ImageFont.truetype('C:/Windows/Fonts/segoeui.ttf', 18)
    font2 = ImageFont.truetype('C:/Windows/Fonts/segoeuib.ttf', 11)
except Exception:
    font = ImageFont.load_default()
    font2 = ImageFont.load_default()

text = 'JEPA WORKSPACE'
text_w = draw.textbbox((0, 0), text, font=font)[2]
draw.text(((420 - text_w) // 2, 42), text, fill=(253, 230, 138, 255), font=font)
draw.text((56, 78), 'Construction operations • delivery • materials • reporting', fill=(226, 232, 240, 255), font=font2)

img.save(out)
print(f'SAVED {out} SIZE {img.size}')

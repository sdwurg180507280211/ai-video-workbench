# 插画版封面：生图网关画的插画（tools/gen_cover.py → assets/cover/原图/，不带字）按原尺寸抠透明，再叠片子字体的标题
# 横 4:3（1440×1080）、竖 3:4（1080×1440）
import importlib.util
import json
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

D = Path(__file__).resolve().parent
FONT = D / 'assets/fonts/NotoSansSC-VF.ttf'
BG, SLATE, MID, ACC, PALE = '#E9EEF2', '#263646', '#5E6E7E', '#FF5A36', '#C8D2DB'
SS = 2                                       # 先画 2 倍再缩小，边缘更干净
BRAND = (json.loads((D / 'film/cues_base.json').read_text(encoding='utf-8')).get('brand') or {}).get('name', '')
SUB = 'AI 画图是从雪花里一点点擦出来的'
_spec = importlib.util.spec_from_file_location('kt', D.parents[1] / '共用/小团子AI素材/抠图.py')
KT = importlib.util.module_from_spec(_spec); _spec.loader.exec_module(KT)


def font(size, weight):
    f = ImageFont.truetype(str(FONT), int(size * SS))
    f.set_variation_by_axes([weight])
    return f


def background(w, h):
    im = Image.new('RGB', (w * SS, h * SS), BG)
    d = ImageDraw.Draw(im)
    step, r = 60 * SS, 2.6 * SS
    for y in range(step // 2, h * SS, step):
        for x in range(step // 2, w * SS, step):
            d.ellipse((x - r, y - r, x + r, y + r), fill=PALE)
    return im


def art(name):
    """按原尺寸抠图（素材库的 抠图.py 会缩到 800，封面不够清楚）。"""
    thumb = Image.Image.thumbnail
    Image.Image.thumbnail = lambda self, *a, **k: None
    try:
        return KT.cut(D / f'assets/cover/原图/{name}.png')
    finally:
        Image.Image.thumbnail = thumb


def place(im, name, width, x, y):
    a = art(name)
    w = int(width * SS)
    a = a.resize((w, int(a.height * w / a.width)), Image.LANCZOS)
    im.alpha_composite(a, (int(x * SS), int(y * SS)))


def title_block(d, x, y, s1, s2, gap):
    """AI 画图，/ 怎么从一团雪花（「一团雪花」垫一道浅橙）/ 变出一张画（「一张画」橙色）。返回最后一行的基线。"""
    f1, f2 = font(s1, 900), font(s2, 900)
    d.text((x * SS, y * SS), 'AI 画图，', font=f1, fill=SLATE, anchor='ls')
    y2 = y + gap
    w0, w1 = d.textlength('怎么从', font=f2), d.textlength('一团雪花', font=f2)
    d.rounded_rectangle((x * SS + w0 - 6 * SS, y2 * SS - s2 * .36 * SS, x * SS + w0 + w1 + 6 * SS, y2 * SS - s2 * .06 * SS), 14 * SS, fill='#FBD3C6')
    d.text((x * SS, y2 * SS), '怎么从一团雪花', font=f2, fill=SLATE, anchor='ls')
    y3 = y2 + gap
    d.text((x * SS, y3 * SS), '变出', font=f2, fill=SLATE, anchor='ls')
    d.text((x * SS + d.textlength('变出', font=f2), y3 * SS), '一张画', font=f2, fill=ACC, anchor='ls')
    return y3


def make(w, h, out):
    im = background(w, h).convert('RGBA')
    if w > h:      # 横 4:3：标题在左上，插画在右下
        place(im, '插画_横', 720, 700, 595)
        d = ImageDraw.Draw(im)
        y3 = title_block(d, 96, 210, 130, 116, 142)
        d.text((100 * SS, (y3 + 84) * SS), SUB, font=font(40, 600), fill=MID, anchor='ls')
        d.text((100 * SS, (h - 70) * SS), BRAND, font=font(40, 800), fill=ACC, anchor='ls')
    else:          # 竖 3:4：标题在上，插画在右下
        place(im, '插画_竖', 680, 360, 620)
        d = ImageDraw.Draw(im)
        y3 = title_block(d, 84, 240, 140, 118, 148)
        d.text((88 * SS, (y3 + 88) * SS), SUB, font=font(44, 600), fill=MID, anchor='ls')
        d.text((88 * SS, (h - 80) * SS), BRAND, font=font(44, 800), fill=ACC, anchor='ls')
    im.convert('RGB').resize((w, h), Image.LANCZOS).save(out, quality=95)
    print(out)


if __name__ == '__main__':
    make(1440, 1080, D / '封面_插画版_横4比3.jpg')
    make(1080, 1440, D / '封面_插画版_竖3比4.jpg')

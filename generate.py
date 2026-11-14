"""
يولّد أيقونات 3D واقعية (زي فولدر B) لكل اسم في subjects.json ويحفظها في icons/<name>.jpg
- مجاني من غير أي مفتاح: Pollinations (موديل Flux).
- لو حطيت GEMINI_API_KEY في Secrets بتاعة المستودع: بيستخدم Gemini (Nano Banana) الأول.
تصميم وتطوير: المهندس إبراهيم فهيم
"""
import base64, io, json, os, sys, time, urllib.parse, urllib.request
from PIL import Image, ImageOps, ImageChops

STYLE = ("Icon of {subject}. Photorealistic glossy 3D product render of a single object, soft studio lighting, "
         "subtle soft shadow under it, centered, the object fills about 80 percent of the frame, isolated on a pure "
         "plain white background, high detail, realistic materials (not plastic, not cartoon), app icon style. "
         "No text, no letters, no logos, no watermark, no cross symbol.")
OUT = 'icons'
SIZE = 512


def http(url, data=None, headers=None, timeout=180):
    req = urllib.request.Request(url, data=data, headers={'User-Agent': 'clinic-icons/1.0', **(headers or {})})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.read()


def gemini(prompt, key):
    model = os.environ.get('GEMINI_MODEL', 'gemini-2.5-flash-image')
    url = f'https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={key}'
    body = json.dumps({'contents': [{'parts': [{'text': prompt}]}],
                       'generationConfig': {'responseModalities': ['IMAGE', 'TEXT']}}).encode()
    res = json.loads(http(url, body, {'Content-Type': 'application/json'}))
    for part in res['candidates'][0]['content']['parts']:
        d = part.get('inlineData') or part.get('inline_data')
        if d and d.get('data'):
            return base64.b64decode(d['data'])
    raise RuntimeError('Gemini returned no image')


def pollinations(prompt, seed):
    q = urllib.parse.quote(prompt, safe='')
    model = os.environ.get('POLLINATIONS_MODEL', 'flux')
    url = f'https://image.pollinations.ai/prompt/{q}?width=1024&height=1024&model={model}&nologo=true&enhance=false&seed={seed}'
    tok = os.environ.get('POLLINATIONS_TOKEN')
    return http(url, headers={'Authorization': 'Bearer ' + tok} if tok else None)


def finish(raw):
    """مربع أبيض 512 والجسم في النص (زي فولدر B)"""
    im = Image.open(io.BytesIO(raw)).convert('RGB')
    w, h = im.size
    s = min(w, h)
    im = im.crop(((w - s) // 2, (h - s) // 2, (w - s) // 2 + s, (h - s) // 2 + s))
    # قص الأبيض الزيادة وبعدين هامش ثابت
    bg = Image.new('RGB', im.size, (255, 255, 255))
    box = ImageChops.difference(im, bg).convert('L').point(lambda p: 255 if p > 18 else 0).getbbox()
    if box:
        obj = im.crop(box)
        side = int(max(obj.size) / 0.84)
        canvas = Image.new('RGB', (side, side), (255, 255, 255))
        canvas.paste(obj, ((side - obj.size[0]) // 2, (side - obj.size[1]) // 2))
        im = canvas
    return im.resize((SIZE, SIZE), Image.LANCZOS)


def main():
    subjects = json.load(open('subjects.json', encoding='utf-8'))
    only = [k.strip() for k in os.environ.get('ONLY', '').split(',') if k.strip()]
    redo = os.environ.get('REDO', 'false').lower() == 'true'
    seed = int(os.environ.get('SEED', '7') or 7)
    key = os.environ.get('GEMINI_API_KEY', '').strip()
    os.makedirs(OUT, exist_ok=True)
    done, failed = [], []
    for name, subject in subjects.items():
        if only and name not in only:
            continue
        path = os.path.join(OUT, name + '.jpg')
        if os.path.exists(path) and not redo and not only:
            continue
        prompt = STYLE.format(subject=subject)
        raw, how = None, ''
        for attempt in range(3):
            try:
                if key:
                    try:
                        raw, how = gemini(prompt, key), 'gemini'
                    except Exception as e:
                        print(f'  gemini failed for {name}: {e}', flush=True)
                if raw is None:
                    raw, how = pollinations(prompt, seed + attempt), 'pollinations'
                finish(raw).save(path, 'JPEG', quality=90, optimize=True, progressive=True)
                break
            except Exception as e:
                raw = None
                print(f'  try {attempt + 1} failed for {name}: {e}', flush=True)
                time.sleep(8 * (attempt + 1))
        if os.path.exists(path) and raw is not None:
            done.append(name)
            print(f'OK  {name}  ({how})', flush=True)
        else:
            failed.append(name)
        time.sleep(3)
    sheet()
    print(f'\nDone: {len(done)}  Failed: {len(failed)} {failed}')
    if failed and not done:
        sys.exit(1)


def sheet():
    """صورة معاينة لكل الأيقونات (preview.jpg)"""
    names = sorted(f for f in os.listdir(OUT) if f.endswith('.jpg'))
    if not names:
        return
    cols, cell = 8, 180
    rows = (len(names) + cols - 1) // cols
    img = Image.new('RGB', (cols * cell, rows * (cell + 24)), (10, 63, 68))
    from PIL import ImageDraw
    d = ImageDraw.Draw(img)
    for i, f in enumerate(names):
        x, y = (i % cols) * cell, (i // cols) * (cell + 24)
        img.paste(Image.open(os.path.join(OUT, f)).resize((cell - 10, cell - 10)), (x + 5, y + 5))
        d.text((x + 8, y + cell - 2), f[:-4], fill=(255, 255, 255))
    img.save('preview.jpg', quality=85)


if __name__ == '__main__':
    main()

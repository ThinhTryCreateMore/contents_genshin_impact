import os
import re
import math
import json
import requests
from io import BytesIO
from PIL import Image, UnidentifiedImageError

null = None
true = True
false = False

# Dán kết quả copy từ ô characters_data vào thay thế mảng bên dưới
CHARACTERS = [
    {"name":"Sigewinne","url":"https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcSYK-mTddBJFEo5JHo0B9LTf4sFo_pnMTGedI5H0ICcBc9xAg2pvHBz_eK4&s=10"}
]
OUT_IMG = "public/assets/characters-sprite.webp"
OUT_CSS = "public/assets/characters.css"
OUT_MAP = "public/assets/sprite-map.json"
ICON_SIZE = 128

os.makedirs(os.path.dirname(OUT_IMG), exist_ok=True)

seen = set()
unique_chars = []
for item in CHARACTERS:
    url = (item.get("url") or "").strip()
    if url and url not in seen:
        seen.add(url)
        unique_chars.append((item.get("name") or "Unknown", url))

session = requests.Session()
session.headers.update({
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
})

def build_candidate_urls(raw_url):
    # Trích xuất Google Drive File ID nếu là link Drive / lh3.google.com
    match = re.search(r"/d/([a-zA-Z0-9_-]+)", raw_url)
    if match and ("google.com" in raw_url or "googleusercontent.com" in raw_url):
        file_id = match.group(1)
        return [
            f"https://drive.google.com/thumbnail?id={file_id}&sz=w256",
            f"https://lh3.googleusercontent.com/d/{file_id}=w256",
            f"https://drive.google.com/uc?export=download&id={file_id}",
        ]
    return [raw_url]

def download_image(raw_url):
    last_err = None
    for candidate in build_candidate_urls(raw_url):
        try:
            resp = session.get(candidate, timeout=15, allow_redirects=True)
            resp.raise_for_status()
            content_type = resp.headers.get("Content-Type", "")
            if "text/html" in content_type:
                last_err = "File chưa bật 'Bất kỳ ai có đường liên kết' trên Google Drive"
                continue
            img = Image.open(BytesIO(resp.content)).convert("RGBA")
            return img.resize((ICON_SIZE, ICON_SIZE), Image.Resampling.LANCZOS)
        except UnidentifiedImageError:
            last_err = "Dữ liệu trả về không phải ảnh (có thể do chưa mở quyền Drive)"
        except Exception as e:
            last_err = str(e)
    raise RuntimeError(last_err or "Không tải được ảnh")

downloaded = []
for i, (name, url) in enumerate(unique_chars):
    try:
        img = download_image(url)
        downloaded.append((name, url, img))
        print(f"[{i+1}/{len(unique_chars)}] OK: {name}")
    except Exception as e:
        print(f"[{i+1}/{len(unique_chars)}] LỖI - {name}: {e}")

total = len(downloaded)
if total == 0:
    raise RuntimeError("Không tải được ảnh nào, hãy kiểm tra lại quyền chia sẻ thư mục Google Drive!")

cols = math.ceil(math.sqrt(total))
rows = math.ceil(total / cols)
sprite = Image.new("RGBA", (cols * ICON_SIZE, rows * ICON_SIZE), (0, 0, 0, 0))

css_lines = [
    ".char-icon {",
    "  display: inline-block;",
    "  width: 64px;",
    "  height: 64px;",
    "  background-image: url('/assets/characters-sprite.webp');",
    f"  background-size: {cols * 100}% {rows * 100}%;",
    "  background-repeat: no-repeat;",
    "}\n"
]
sprite_map = {}

for idx, (name, url, img) in enumerate(downloaded):
    col = idx % cols
    row = idx // cols
    sprite.paste(img, (col * ICON_SIZE, row * ICON_SIZE))

    class_name = f"char-{idx}"
    pos_x = (col / (cols - 1) * 100) if cols > 1 else 0
    pos_y = (row / (rows - 1) * 100) if rows > 1 else 0

    css_lines.append(f"/* {name} */")
    css_lines.append(f".{class_name} {{ background-position: {pos_x:.4f}% {pos_y:.4f}%; }}")
    sprite_map[url] = class_name

sprite.save(OUT_IMG, "WEBP", quality=82, method=6)
with open(OUT_CSS, "w", encoding="utf-8") as f:
    f.write("\n".join(css_lines))
with open(OUT_MAP, "w", encoding="utf-8") as f:
    json.dump(sprite_map, f, indent=2, ensure_ascii=False)

print(f"\nHoàn tất! Đã đóng gói {total}/{len(unique_chars)} icon vào {OUT_IMG}")
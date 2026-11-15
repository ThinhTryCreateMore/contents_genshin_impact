#!/usr/bin/env python3
"""
build_sprite.py
Tải toàn bộ ảnh icon nhân vật (tự động chuyển đổi link Google Drive /u/0/d/ bị khóa cookie,
thêm User-Agent chuẩn trình duyệt, dự phòng Enka CDN hoặc ảnh chữ cái nổi nếu link gốc lỗi)
và ghép thành 1 CSS Sprite Sheet duy nhất trong thư mục assets/.

Cách chạy:
  pip install requests pillow
  python build_sprite.py
"""

import io
import json
import math
import os
import re
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

try:
    import requests
    from PIL import Image, ImageDraw, ImageFont, ImageOps
except ImportError:
    print("Thiếu thư viện! Hãy chạy lệnh: pip install requests pillow")
    sys.exit(1)

BASE_DIR = Path(__file__).resolve().parent
INPUT_JSON = BASE_DIR / "characters_icons.json"
ASSETS_DIR = BASE_DIR / "assets"
SPRITE_WEBP = ASSETS_DIR / "characters.webp"
SPRITE_PNG = ASSETS_DIR / "characters.png"
SPRITE_CSS = ASSETS_DIR / "characters.css"
SPRITE_MAP_JSON = ASSETS_DIR / "sprite-map.json"

TILE_SIZE = 128
COLS = 12  # 12 cột -> 116 nhân vật chỉ mất 10 hàng (1536x1280px, cực nhẹ!)

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/131.0.0.0 Safari/537.36"
    ),
    "Accept": "image/avif,image/webp,image/apng,image/*,*/*;q=0.8",
    "Accept-Language": "vi-VN,vi;q=0.9,en-US;q=0.8,en;q=0.7",
}

CDN_SLUG_OVERRIDES = {
    "traveller": "PlayerBoy",
    "traveler": "PlayerBoy",
    "aether": "PlayerBoy",
    "lumine": "PlayerGirl",
    "nhà lữ hành": "PlayerBoy",
    "nha lu hanh": "PlayerBoy",
    "hu tao": "Hutao",
    "raiden shogun": "Shougun",
    "raiden": "Shougun",
    "kamisato ayaka": "Ayaka",
    "kamisato ayato": "Ayato",
    "kaedehara kazuha": "Kazuha",
    "sangonomiya kokomi": "Kokomi",
    "arataki itto": "Itto",
    "kujou sara": "Sara",
    "kuki shinobu": "Shinobu",
    "shikanoin heizou": "Heizou",
    "yae miko": "Yae",
    "yoimiya": "Yoimiya",
    "kirara": "Momoka",
    "chiori": "Chiori",
    "thoma": "Tohma",
    "gorou": "Gorou",
    "sayu": "Sayu",
    "yun jin": "Yunjin",
    "yanfei": "Feiyan",
    "xianyun": "Liuyun",
    "baizhu": "Baizhuer",
    "alhaitham": "Alhatham",
    "wanderer": "Wanderer",
    "scaramouche": "Wanderer",
    "lyney": "Liney",
    "lynette": "Linette",
    "freminet": "Freminet",
    "neuvillette": "Neuvillette",
    "wriothesley": "Wriothesley",
    "furina": "Furina",
    "charlotte": "Charlotte",
    "navia": "Navia",
    "chevreuse": "Chevreuse",
    "gaming": "Gaming",
    "arlecchino": "Arlecchino",
    "clorinde": "Clorinde",
    "sigewinne": "Sigewinne",
    "emilie": "Emilie",
    "kachina": "Kachina",
    "kinich": "Kinich",
    "mualani": "Mualani",
    "xilonen": "Xilonen",
    "chasca": "Chasca",
    "ororon": "Olorun",
    "mavuika": "Mavuika",
    "citlali": "Citlali",
    "lan yan": "Lanyan",
    "yumemizuki mizuki": "Mizuki",
    "varesa": "Varesa",
    "iansan": "Iansan",
    "escoffier": "Escoffier",
    "ifa": "Ifa",
    "skirk": "Skirk",
    "dahlia": "Dahlia",
    "ineffa": "Ineffa",
    "aino": "Aino",
    "flins": "Flins",
    "lauma": "Lauma",
    "nefer": "Nefer",
    "jahoda": "Jahoda",
    "durin": "Durin",
    "columbina": "Columbina",
    "zibai": "Zibai",
    "illuga": "Illuga",
    "varka": "Varka",
    "linnea": "Linnea",
    "nicole": "Nicole",
    "sandrone": "Sandrone",
    "jean": "Qin",
    "amber": "Ambor",
    "noelle": "Noel",
    "ningguang": "Ningguang",
    "xingqiu": "Xingqiu",
    "chongyun": "Chongyun",
    "tartaglia": "Tartaglia",
    "childe": "Tartaglia",
}


def slugify(name: str) -> str:
    s = re.sub(r"[^a-zA-Z0-9]+", "-", name.strip().lower()).strip("-")
    return s or "char"


def extract_gdrive_id(url: str) -> str | None:
    patterns = [
        r"lh3\.google\.com/u/\d+/d/([a-zA-Z0-9_-]+)",
        r"lh3\.googleusercontent\.com/d/([a-zA-Z0-9_-]+)",
        r"drive\.google\.com/file/d/([a-zA-Z0-9_-]+)",
        r"drive\.google\.com/open\?id=([a-zA-Z0-9_-]+)",
        r"drive\.google\.com/uc\?[^#]*id=([a-zA-Z0-9_-]+)",
    ]
    for pat in patterns:
        m = re.search(pat, url)
        if m:
            return m.group(1)
    return None


def get_enka_fallback_url(name: str) -> str:
    lower = name.strip().lower()
    slug = CDN_SLUG_OVERRIDES.get(lower)
    if not slug:
        parts = name.strip().split()
        last = re.sub(r"[^a-zA-Z0-9]", "", parts[-1]) if parts else ""
        slug = last[0].upper() + last[1:] if last else ""
    return f"https://enka.network/ui/UI_AvatarIcon_{slug}.png" if slug else ""


def build_candidate_urls(name: str, raw_url: str) -> list[str]:
    candidates = []
    gdrive_id = extract_gdrive_id(raw_url)
    if gdrive_id:
        # Ưu tiên endpoint công khai không dính cookie /u/0/
        candidates.extend([
            f"https://lh3.googleusercontent.com/d/{gdrive_id}=s256",
            f"https://drive.google.com/thumbnail?id={gdrive_id}&sz=w256",
            f"https://drive.google.com/uc?export=view&id={gdrive_id}",
        ])
    if raw_url and "pinterest.com/pin/" not in raw_url:
        candidates.append(raw_url)

    enka_url = get_enka_fallback_url(name)
    if enka_url:
        candidates.append(enka_url)

    # Loại trùng nhưng giữ nguyên thứ tự ưu tiên
    seen = set()
    unique = []
    for u in candidates:
        if u and u not in seen:
            seen.add(u)
            unique.append(u)
    return unique


def create_monogram_tile(name: str) -> Image.Image:
    """Tạo avatar chữ cái nền xanh-vàng sang trọng nếu cả link gốc lẫn CDN đều không có ảnh."""
    img = Image.new("RGBA", (TILE_SIZE, TILE_SIZE), (17, 36, 54, 255))
    draw = ImageDraw.Draw(img)
    draw.ellipse((6, 6, TILE_SIZE - 6, TILE_SIZE - 6), fill=(24, 50, 74, 255), outline=(236, 194, 101, 255), width=4)
    initial = (name.strip()[:1] or "?").upper()
    try:
        font = ImageFont.truetype("arialbd.ttf", 56)
    except Exception:
        font = ImageFont.load_default()
    bbox = draw.textbbox((0, 0), initial, font=font)
    tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
    draw.text(((TILE_SIZE - tw) / 2, (TILE_SIZE - th) / 2 - 4), initial, fill=(255, 226, 148, 255), font=font)
    return img


def fetch_and_prepare_tile(idx: int, item: dict) -> tuple[int, str, str, Image.Image, str]:
    name = item["name"].strip()
    raw_url = item.get("url", "").strip()
    candidates = build_candidate_urls(name, raw_url)

    for cand_url in candidates:
        try:
            req_headers = dict(HEADERS)
            if "redd.it" in cand_url:
                req_headers["Referer"] = "https://www.reddit.com/"
            elif "hoyolab.com" in cand_url:
                req_headers["Referer"] = "https://www.hoyolab.com/"
            elif "pinimg.com" in cand_url:
                req_headers["Referer"] = "https://www.pinterest.com/"

            resp = requests.get(cand_url, headers=req_headers, timeout=12, allow_redirects=True)
            ctype = resp.headers.get("Content-Type", "").lower()
            if resp.status_code == 200 and ("image" in ctype or len(resp.content) > 800):
                im = Image.open(io.BytesIO(resp.content)).convert("RGBA")
                # Cắt vuông ưu tiên phần đầu/mặt nhân vật phía trên (centering=(0.5, 0.2))
                tile = ImageOps.fit(im, (TILE_SIZE, TILE_SIZE), method=Image.Resampling.LANCZOS, centering=(0.5, 0.2))
                source_tag = "GDrive/Gốc" if cand_url != get_enka_fallback_url(name) else "Enka CDN"
                return idx, name, raw_url, tile, f"OK ({source_tag})"
        except Exception:
            continue

    return idx, name, raw_url, create_monogram_tile(name), "FALLBACK (Monogram)"


def main():
    if not INPUT_JSON.exists():
        print(f"Không tìm thấy file {INPUT_JSON}!")
        sys.exit(1)

    with open(INPUT_JSON, "r", encoding="utf-8") as f:
        items = json.load(f)

    ASSETS_DIR.mkdir(parents=True, exist_ok=True)
    total = len(items)
    print(f"Đang tải và xử lý {total} nhân vật...")

    results = [None] * total
    with ThreadPoolExecutor(max_workers=12) as pool:
        futures = [pool.submit(fetch_and_prepare_tile, i, item) for i, item in enumerate(items)]
        for fut in as_completed(futures):
            idx, name, raw_url, tile, status = fut.result()
            results[idx] = (name, raw_url, tile, status)
            print(f"[{idx + 1:03d}/{total:03d}] {name:<22} -> {status}")

    rows = math.ceil(total / COLS)
    sheet_w = COLS * TILE_SIZE
    sheet_h = rows * TILE_SIZE
    sheet = Image.new("RGBA", (sheet_w, sheet_h), (0, 0, 0, 0))

    sprite_map = {}
    css_lines = [
        "/* Tự động sinh bởi build_sprite.py — Hỗ trợ đa kích thước (22px, 34px, 54px, 112px) */",
        ".char-icon {",
        "  display: inline-block;",
        "  background-image: url('/assets/characters.webp');",
        "  background-repeat: no-repeat;",
        f"  background-size: {COLS * 100}% {rows * 100}%;",
        "}",
        ""
    ]

    used_slugs = set()
    monogram_list = []

    for i, (name, raw_url, tile, status) in enumerate(results):
        if "Monogram" in status:
            monogram_list.append(name)

        col = i % COLS
        row = i // COLS
        sheet.paste(tile, (col * TILE_SIZE, row * TILE_SIZE))

        base_slug = slugify(name)
        cls_slug = base_slug
        counter = 2
        while cls_slug in used_slugs:
            cls_slug = f"{base_slug}-{counter}"
            counter += 1
        used_slugs.add(cls_slug)
        cls_name = f"icon-{cls_slug}"

        pos_x = (col / (COLS - 1) * 100) if COLS > 1 else 0.0
        pos_y = (row / (rows - 1) * 100) if rows > 1 else 0.0
        css_lines.append(f".char-icon.{cls_name} {{ background-position: {pos_x:.4f}% {pos_y:.4f}%; }}")

        # Ánh xạ đa khóa để web luôn khớp sprite dù URL có thay đổi query params
        if raw_url:
            sprite_map[raw_url] = cls_name
        gdrive_id = extract_gdrive_id(raw_url)
        if gdrive_id:
            sprite_map[f"https://lh3.googleusercontent.com/d/{gdrive_id}=s256"] = cls_name
        sprite_map[name] = cls_name
        sprite_map[name.lower()] = cls_name

    # Xuất WebP tối ưu dung lượng (~350-500KB cho toàn bộ 116 nhân vật)
    sheet.save(SPRITE_WEBP, "WEBP", quality=86, method=6)
    SPRITE_CSS.write_text("\n".join(css_lines) + "\n", encoding="utf-8")
    SPRITE_MAP_JSON.write_text(json.dumps(sprite_map, ensure_ascii=False, indent=2), encoding="utf-8")

    print("\n" + "=" * 60)
    print(f"HOÀN TẤT! Đã ghép {total} nhân vật vào:")
    print(f"  - {SPRITE_WEBP} ({SPRITE_WEBP.stat().st_size // 1024} KB)")
    print(f"  - {SPRITE_CSS}")
    print(f"  - {SPRITE_MAP_JSON}")
    if monogram_list:
        print(f"\nLưu ý: {len(monogram_list)} nhân vật dùng avatar chữ cái (do link Drive riêng tư): {', '.join(monogram_list)}")
    print("=" * 60)


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
from __future__ import annotations

import html
import json
import re
import shutil
import urllib.parse
import urllib.request
from pathlib import Path

WP_API_URL = "https://queertheater.mycafe24.com/wp-json/wp/v2"
SITE_URL = "https://queertheater.kr"
OUTPUT_DIR = Path(__file__).resolve().parents[1] / "share"
FALLBACK_IMAGE = f"{SITE_URL}/og-image.png"


def fetch_json(url: str):
    req = urllib.request.Request(
        url,
        headers={
            "User-Agent": "queertheater-share-generator/1.0",
            "Accept": "application/json",
        },
    )
    with urllib.request.urlopen(req, timeout=30) as response:
        return json.load(response)


def fetch_performances():
    all_items = []
    page = 1

    while True:
        url = f"{WP_API_URL}/performance?per_page=100&page={page}&_fields=id,title,acf"
        try:
            items = fetch_json(url)
        except urllib.error.HTTPError as exc:
            # WP returns 400 when requesting a page beyond the last page.
            if exc.code == 400 and page > 1:
                break
            raise

        if not items:
            break

        all_items.extend(items)

        if len(items) < 100:
            break

        page += 1
        if page > 50:
            raise RuntimeError("Too many WordPress pages; stopping for safety.")

    return all_items


def strip_html(value: str) -> str:
    value = re.sub(r"<[^>]+>", " ", value or "")
    value = html.unescape(value)
    return re.sub(r"\s+", " ", value).strip()


def poster_url(acf: dict) -> str:
    raw = acf.get("poster")
    if isinstance(raw, dict):
        raw = raw.get("url", "")
    if isinstance(raw, str) and raw.strip():
        return urllib.parse.urljoin(SITE_URL, raw.strip())
    return FALLBACK_IMAGE


def description_for(acf: dict) -> str:
    description = strip_html(str(acf.get("description") or ""))
    if description:
        return description[:240]

    bits = []
    for key in ("date", "venue", "production"):
        value = strip_html(str(acf.get(key) or ""))
        if value:
            bits.append(value)

    if bits:
        return " · ".join(bits)[:240]

    return "한국 퀴어 연극 아카이브의 공연 기록입니다."


def render_page(item: dict) -> str:
    performance_id = int(item["id"])
    title = strip_html(item.get("title", {}).get("rendered", "")) or "한국 퀴어 연극 아카이브"
    acf = item.get("acf") or {}
    image = poster_url(acf)
    description = description_for(acf)

    share_url = f"{SITE_URL}/share/{performance_id}/"
    detail_url = f"{SITE_URL}/#detail/{performance_id}"

    title_attr = html.escape(title, quote=True)
    desc_attr = html.escape(description, quote=True)
    image_attr = html.escape(image, quote=True)
    share_attr = html.escape(share_url, quote=True)
    detail_attr = html.escape(detail_url, quote=True)

    return f"""<!doctype html>
<html lang="ko">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width,initial-scale=1">

  <title>{title_attr} — 한국 퀴어 연극 아카이브</title>
  <meta name="description" content="{desc_attr}">
  <link rel="canonical" href="{share_attr}">

  <meta property="og:type" content="website">
  <meta property="og:site_name" content="한국 퀴어 연극 아카이브">
  <meta property="og:locale" content="ko_KR">
  <meta property="og:title" content="{title_attr}">
  <meta property="og:description" content="{desc_attr}">
  <meta property="og:url" content="{share_attr}">
  <meta property="og:image" content="{image_attr}">
  <meta property="og:image:alt" content="{title_attr} 포스터">

  <meta name="twitter:card" content="summary_large_image">
  <meta name="twitter:title" content="{title_attr}">
  <meta name="twitter:description" content="{desc_attr}">
  <meta name="twitter:image" content="{image_attr}">

  <style>
    html, body {{ margin: 0; min-height: 100%; background: #fff; color: #111; }}
    body {{
      display: grid;
      place-items: center;
      padding: 28px;
      font-family: "Noto Sans KR", "Apple SD Gothic Neo", Arial, sans-serif;
    }}
    main {{ width: min(560px, 100%); }}
    img {{ display: block; width: min(320px, 76vw); height: auto; margin: 0 0 24px; }}
    h1 {{ margin: 0 0 12px; font-size: 24px; line-height: 1.25; word-break: keep-all; }}
    p {{ line-height: 1.7; }}
    a {{ color: inherit; }}
  </style>

  <script>
    // SNS crawler는 위의 정적 OG 태그를 읽고,
    // 사람의 브라우저만 실제 작품 상세 화면으로 이동합니다.
    window.addEventListener('DOMContentLoaded', function () {{
      window.location.replace({json.dumps(detail_url, ensure_ascii=False)});
    }});
  </script>
</head>
<body>
  <main>
    <img src="{image_attr}" alt="{title_attr} 포스터">
    <h1>{title_attr}</h1>
    <p>{desc_attr}</p>
    <p><a href="{detail_attr}">작품 기록 보기 →</a></p>
  </main>
</body>
</html>
"""


def main():
    performances = fetch_performances()
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    live_ids = set()

    for item in performances:
        performance_id = int(item["id"])
        live_ids.add(str(performance_id))
        target_dir = OUTPUT_DIR / str(performance_id)
        target_dir.mkdir(parents=True, exist_ok=True)
        (target_dir / "index.html").write_text(render_page(item), encoding="utf-8")

    # Remove stale numeric share pages if a performance disappears.
    for child in OUTPUT_DIR.iterdir():
        if child.is_dir() and child.name.isdigit() and child.name not in live_ids:
            shutil.rmtree(child)

    print(f"Generated {len(performances)} performance share pages in {OUTPUT_DIR}")


if __name__ == "__main__":
    main()

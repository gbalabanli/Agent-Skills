#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
from datetime import datetime
from pathlib import Path

from playwright.sync_api import TimeoutError as PlaywrightTimeoutError
from playwright.sync_api import sync_playwright


BASE_URL = (
    "https://www.sahibinden.com/"
    "satilik-daire/istanbul-maltepe-kucukyali-altintepe-mh."
    "?sorting=price_asc&a20=38470"
)
PAGES_TO_SCRAPE = 10
CHROME_PATH = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
PROFILE_DIR = Path("temp_pw_profile")


def extract_rows(page_no: int, page) -> list[dict]:
    rows = page.eval_on_selector_all(
        "table tr",
        """(rows, pageNo) => {
          const out = [];
          for (const tr of rows) {
            const cells = Array.from(tr.querySelectorAll('td'));
            const titleLink = tr.querySelector('a[href*="/ilan/"]');
            if (cells.length < 7 || !titleLink) continue;

            const title = (titleLink.getAttribute('title') || titleLink.textContent || '')
              .replace(/\\s+/g, ' ')
              .trim();
            const href = titleLink.getAttribute('href');
            const rooms = (cells[3]?.textContent || '').trim();
            if (!title || !href || rooms !== '2+1') continue;

            out.push({
              page_no: pageNo,
              title,
              url: href.startsWith('http') ? href : `https://www.sahibinden.com${href}`,
              size_sqm_brut: (cells[2]?.textContent || '').trim(),
              rooms,
              price_text: (cells[4]?.textContent || '').trim(),
              date: (cells[5]?.textContent || '').replace(/\\s+/g, ' ').trim(),
              neighborhood: (cells[6]?.textContent || '').trim(),
            });
          }
          return out;
        }""",
        page_no,
    )
    return rows


def price_key(item: dict) -> int:
    digits = "".join(ch for ch in item.get("price_text", "") if ch.isdigit())
    return int(digits) if digits else 10**18


def main() -> int:
    PROFILE_DIR.mkdir(exist_ok=True)
    items: list[dict] = []
    page_summaries: list[dict] = []

    with sync_playwright() as pw:
        context = pw.chromium.launch_persistent_context(
            user_data_dir=str(PROFILE_DIR.resolve()),
            executable_path=CHROME_PATH,
            headless=False,
        )
        try:
            page = context.pages[0] if context.pages else context.new_page()

            for index in range(PAGES_TO_SCRAPE):
                offset = index * 20
                url = f"{BASE_URL}&pagingOffset={offset}" if offset else BASE_URL
                page.goto(url, wait_until="domcontentloaded", timeout=120000)
                page.wait_for_selector("table", timeout=30000)
                rows = extract_rows(index + 1, page)
                page_summaries.append(
                    {
                        "page": index + 1,
                        "url": page.url,
                        "count": len(rows),
                    }
                )
                items.extend(rows)

        except PlaywrightTimeoutError as exc:
            print(f"[ERROR] Timed out while scraping: {exc}")
            return 1
        finally:
            context.close()

    items.sort(key=price_key)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    json_path = Path(f"sahibinden_altintepe_2plus1_price_asc_{timestamp}.json")
    csv_path = Path(f"sahibinden_altintepe_2plus1_price_asc_{timestamp}.csv")

    payload = {
        "source": BASE_URL,
        "pages": page_summaries,
        "total": len(items),
        "items": items,
    }
    json_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")

    with csv_path.open("w", newline="", encoding="utf-8-sig") as handle:
        fieldnames = [
            "page_no",
            "title",
            "url",
            "size_sqm_brut",
            "rooms",
            "price_text",
            "date",
            "neighborhood",
        ]
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(items)

    print(json.dumps({"json": str(json_path), "csv": str(csv_path), "total": len(items)}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

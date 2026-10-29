"""Blitz TokyoInsider Scraper API — Author: Blitz (@blitzlabx)"""
import re
from urllib.parse import urljoin

from bs4 import BeautifulSoup

from .crypto import decode_link, extract_key

DECOY = "f2829db49"
KIND_RE = re.compile(r"/(episode|movie|ova|special)/(\d+)", re.I)
SERIES_RE = re.compile(r"^/anime/([A-Za-z0-9])/([^/]+)$")
FILENAME_DROP_RE = re.compile(r'<i class="%s"[^>]*>.*?</i>' % DECOY, re.S)


def soup(html: str) -> BeautifulSoup:
    return BeautifulSoup(html, "lxml")


def clean_filename(raw_html: str) -> str:
    stripped = FILENAME_DROP_RE.sub("", raw_html)
    return " ".join(BeautifulSoup(stripped, "lxml").get_text().split())


def _text(node) -> str | None:
    if node is None:
        return None
    value = " ".join(node.get_text(" ").split())
    return value or None


def parse_anime(html: str, base: str) -> dict:
    doc = soup(html)

    def table_value(label: str) -> str | None:
        for row in doc.select("table tr"):
            cells = row.find_all("td")
            if len(cells) >= 2 and cells[0].get_text(strip=True).lower().startswith(label):
                return _text(cells[1])
        return None

    titles: list[str] = []
    for row in doc.select("table tr"):
        cells = row.find_all("td")
        if cells and cells[0].get_text(strip=True).lower().startswith("title"):
            for chunk in cells[1].get_text("\n").split("\n"):
                if chunk.strip():
                    titles.append(chunk.strip())

    creator = None
    for anchor in doc.select("table a[href*='/anime/search?c=']"):
        creator = _text(anchor)
        break

    genres = [
        {"name": _text(a), "url": urljoin(base, a.get("href"))}
        for a in doc.select("table a[href*='/anime/search?g=']")
    ]

    ratings: dict[str, str] = {}
    for row in doc.select("table tr"):
        cells = row.find_all("td")
        if len(cells) >= 3:
            link = cells[2].find("a")
            if link and "/reviews/" in link.get("href", ""):
                ratings[_text(cells[0]) or "?"] = _text(cells[2]) or ""

    cover = doc.select_one("a[href*='/anime/'] img[src*='/upload/covers/']")
    rss = doc.select_one("a[href*='/rss/']")

    related = []
    seen = set()
    for anchor in doc.select("a[href^='/anime/']"):
        href = anchor.get("href", "")
        if KIND_RE.search(href) or "search" in href or anchor.find("img") is not None:
            continue
        title = _text(anchor)
        if not title or href in seen:
            continue
        seen.add(href)
        related.append({"title": title, "url": urljoin(base, href)})

    return {
        "title": titles[0] if titles else None,
        "titles": titles,
        "cover": urljoin(base, cover.get("src")) if cover and cover.get("src") else None,
        "rss": urljoin(base, rss.get("href")) if rss and rss.get("href") else None,
        "creator": creator,
        "genres": genres,
        "age_group": table_value("age"),
        "vintage": table_value("vintage"),
        "status": table_value("status"),
        "summary": table_value("summary"),
        "ratings": ratings,
        "related": related[:40],
    }


def parse_listing_downloads(html: str, base: str) -> list[dict]:
    doc = soup(html)
    key = extract_key(html)
    out = []
    for span in doc.select("span.download-link, span.dlk, span.lk"):
        part_a, part_b = span.get("data-a"), span.get("data-b")
        if not part_a or not part_b:
            continue
        row = span.find_parent("tr") or span.parent
        kind = number = None
        for anchor in row.select("a[href]"):
            match = KIND_RE.search(anchor.get("href", ""))
            if match:
                kind, number = match.group(1).lower(), int(match.group(2))
                break
        filename = clean_filename(str(span))
        item = {
            "kind": kind,
            "number": number,
            "label": filename,
            "filename": filename,
            "page_url": None,
        }
        if kind and number:
            item["page_url"] = f"{base}/anime/{{letter}}/{{name}}/{kind}/{number}"
        try:
            item["url"] = decode_link(part_a, part_b, key)
        except Exception as exc:  # noqa: BLE001
            item["url"] = None
            item["error"] = str(exc)
        out.append(item)
    return out


def parse_episode(html: str) -> dict:
    doc = soup(html)
    key = extract_key(html)
    files = []
    for span in doc.select("span.dlk"):
        part_a, part_b = span.get("data-a"), span.get("data-b")
        if not part_a or not part_b:
            continue
        block = span.find_parent("div")
        info: dict[str, str] = {}
        finfo = block.select_one(".finfo") if block else None
        if finfo:
            raw = str(finfo)
            for label in ("Size", "Downloads", "Uploader", "Added On"):
                match = re.search(rf"{label}:\s*<b>(.*?)</b>", raw, re.S)
                if match:
                    info[label.lower().replace(" ", "_")] = match.group(1).strip()
        comment = block.select_one("a[href*='/comment']") if block else None
        entry = {
            "filename": clean_filename(str(span)),
            "comments_url": comment.get("href") if comment else None,
        }
        entry.update(info)
        try:
            entry["url"] = decode_link(part_a, part_b, key)
        except Exception as exc:  # noqa: BLE001
            entry["url"] = None
            entry["error"] = str(exc)
        files.append(entry)

    prev_link = doc.select_one("a.nfl")
    next_link = doc.select_one("a.nfr")
    return {
        "heading": _text(doc.select_one(".c_h1")),
        "files": files,
        "prev": _text(prev_link),
        "next": _text(next_link),
        "prev_url": prev_link.get("href") if prev_link else None,
        "next_url": next_link.get("href") if next_link else None,
    }


def parse_search(html: str, base: str) -> list[dict]:
    doc = soup(html)
    results, seen = [], set()
    for anchor in doc.select("a[href]"):
        href = anchor.get("href", "")
        match = SERIES_RE.search(href)
        if not match or "/reviews" in href or href in seen:
            continue
        title = _text(anchor)
        if not title:
            continue
        seen.add(href)
        cover = anchor.find("img")
        results.append(
            {
                "title": title,
                "url": urljoin(base, href),
                "letter": match.group(1),
                "slug": match.group(2),
                "cover": urljoin(base, cover.get("src")) if cover and cover.get("src") else None,
            }
        )
    return results


def parse_new(html: str, base: str) -> list[dict]:
    rows = [i for i in parse_listing_downloads(html, base) if i.get("kind")]
    if rows:
        return rows
    doc = soup(html)
    for anchor in doc.select("a[href]"):
        match = KIND_RE.search(anchor.get("href", ""))
        if match:
            rows.append(
                {
                    "label": _text(anchor),
                    "kind": match.group(1).lower(),
                    "number": int(match.group(2)),
                    "url": urljoin(base, anchor.get("href")),
                }
            )
    return rows


def parse_pagination(html: str) -> dict:
    doc = soup(html)
    starts = []
    for anchor in doc.select("a[href*='start=']"):
        match = re.search(r"start=(\d+)", anchor.get("href", ""))
        if match:
            starts.append(int(match.group(1)))
    return {"next_start": max(starts) if starts else None, "has_more": bool(starts)}

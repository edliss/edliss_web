#!/usr/bin/env python3
"""Generate the Edliss Notes RSS feed from the static Notes HTML."""

from __future__ import annotations

import argparse
import re
import sys
from dataclasses import dataclass
from datetime import date, datetime, time, timezone
from email.utils import format_datetime, parsedate_to_datetime
from html import unescape
from html.parser import HTMLParser
from pathlib import Path
from typing import Iterable
from urllib.parse import urljoin
from xml.etree import ElementTree as ET


SITE_ROOT = "https://edliss.com"
NOTES_URL = f"{SITE_ROOT}/notes/"
FEED_URL = f"{NOTES_URL}feed.xml"
FEED_TITLE = "Edliss Notes"
FEED_DESCRIPTION = "Notes on building thoughtful software."
FEED_LANGUAGE = "en"
EXCERPT_LENGTH = 180

ATOM_NS = "http://www.w3.org/2005/Atom"
CONTENT_NS = "http://purl.org/rss/1.0/modules/content/"


@dataclass
class Note:
    title: str
    href: str
    published: date
    excerpt: str
    content_html: str
    position: int

    @property
    def url(self) -> str:
        return urljoin(SITE_ROOT, self.href)


class NotesIndexParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.notes: list[dict[str, str]] = []
        self.current: dict[str, str] | None = None
        self.capture: str | None = None
        self.buffer: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        attr = dict(attrs)
        classes = set((attr.get("class") or "").split())

        if tag == "a" and "note-card" in classes:
            self.current = {"href": attr.get("href") or ""}
            return

        if self.current is None:
            return

        if tag == "time":
            self.current["date"] = attr.get("datetime") or ""
        elif tag in {"h2", "p"}:
            self.capture = "title" if tag == "h2" else "excerpt"
            self.buffer = []

    def handle_data(self, data: str) -> None:
        if self.current is not None and self.capture:
            self.buffer.append(data)

    def handle_endtag(self, tag: str) -> None:
        if self.current is None:
            return

        if self.capture and tag in {"h2", "p"}:
            self.current[self.capture] = normalize_text("".join(self.buffer))
            self.capture = None
            self.buffer = []
        elif tag == "a":
            self.notes.append(self.current)
            self.current = None


class TextExtractor(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.parts: list[str] = []

    def handle_data(self, data: str) -> None:
        self.parts.append(data)

    @property
    def text(self) -> str:
        return normalize_text(" ".join(self.parts))


class MetaParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.description = ""

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag != "meta":
            return

        attr = dict(attrs)
        if attr.get("name") == "description":
            self.description = attr.get("content") or ""


def normalize_text(value: str) -> str:
    return re.sub(r"\s+", " ", unescape(value)).strip()


def strip_markup(value: str) -> str:
    value = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", value)
    value = re.sub(r"[`*_#>~-]+", "", value)

    extractor = TextExtractor()
    extractor.feed(value)
    return normalize_text(extractor.text or value)


def truncate(value: str, length: int = EXCERPT_LENGTH) -> str:
    value = normalize_text(value)
    if len(value) <= length:
        return value

    shortened = value[: length + 1].rsplit(" ", 1)[0].rstrip(".,;:")
    return f"{shortened}..."


def read_notes_index(root: Path) -> list[dict[str, str]]:
    parser = NotesIndexParser()
    parser.feed((root / "notes" / "index.html").read_text(encoding="utf-8"))
    return parser.notes


def extract_article_html(html: str) -> str:
    match = re.search(
        r'<article\s+class="note-body">\s*(.*?)\s*</article>',
        html,
        flags=re.DOTALL | re.IGNORECASE,
    )
    if not match:
        return ""

    content = match.group(1).strip()
    return absolutize_root_relative_links(content)


def absolutize_root_relative_links(html: str) -> str:
    return re.sub(r'(href|src)="(/[^"]*)"', rf'\1="{SITE_ROOT}\2"', html)


def first_paragraph_text(html: str) -> str:
    match = re.search(r"<p\b[^>]*>(.*?)</p>", html, flags=re.DOTALL | re.IGNORECASE)
    return strip_markup(match.group(1)) if match else ""


def page_description(html: str) -> str:
    parser = MetaParser()
    parser.feed(html)
    return normalize_text(parser.description)


def parse_note(root: Path, index_note: dict[str, str], position: int) -> Note:
    href = index_note.get("href", "")
    page_path = root / href.lstrip("/") / "index.html"
    html = page_path.read_text(encoding="utf-8")
    content_html = extract_article_html(html)

    excerpt = (
        normalize_text(index_note.get("excerpt", ""))
        or first_paragraph_text(content_html)
        or page_description(html)
    )

    return Note(
        title=normalize_text(index_note.get("title", "")),
        href=href,
        published=date.fromisoformat(index_note.get("date", "")),
        excerpt=truncate(strip_markup(excerpt)),
        content_html=content_html,
        position=position,
    )


def pub_date(value: date) -> str:
    return format_datetime(datetime.combine(value, time.min, tzinfo=timezone.utc))


def build_feed(notes: Iterable[Note]) -> str:
    ET.register_namespace("atom", ATOM_NS)
    ET.register_namespace("content", CONTENT_NS)

    rss = ET.Element("rss", {"version": "2.0"})
    channel = ET.SubElement(rss, "channel")
    ET.SubElement(channel, "title").text = FEED_TITLE
    ET.SubElement(channel, "link").text = NOTES_URL
    ET.SubElement(
        channel,
        f"{{{ATOM_NS}}}link",
        {"href": FEED_URL, "rel": "self", "type": "application/rss+xml"},
    )
    ET.SubElement(channel, "description").text = FEED_DESCRIPTION
    ET.SubElement(channel, "language").text = FEED_LANGUAGE
    ET.SubElement(channel, "lastBuildDate").text = format_datetime(datetime.now(timezone.utc))

    for note in notes:
        item = ET.SubElement(channel, "item")
        ET.SubElement(item, "title").text = note.title
        ET.SubElement(item, "link").text = note.url
        ET.SubElement(item, "guid", {"isPermaLink": "true"}).text = note.url
        ET.SubElement(item, "pubDate").text = pub_date(note.published)
        ET.SubElement(item, "description").text = note.excerpt
        if note.content_html:
            ET.SubElement(item, f"{{{CONTENT_NS}}}encoded").text = note.content_html

    ET.indent(rss, space="  ")
    xml = ET.tostring(rss, encoding="unicode", short_empty_elements=True)
    return f'<?xml version="1.0" encoding="UTF-8"?>\n{xml}\n'


def generate(root: Path) -> str:
    index_notes = read_notes_index(root)
    notes = [parse_note(root, note, position) for position, note in enumerate(index_notes)]
    notes.sort(key=lambda note: note.published, reverse=True)
    return build_feed(notes)


def validate_feed(xml: str) -> None:
    root = ET.fromstring(xml)
    if root.tag != "rss" or root.get("version") != "2.0":
        raise ValueError("Feed root must be <rss version=\"2.0\">.")

    channel = root.find("channel")
    if channel is None:
        raise ValueError("Feed is missing <channel>.")

    for tag in ("title", "link", "description", "language", "lastBuildDate"):
        if not (channel.findtext(tag) or "").strip():
            raise ValueError(f"Channel is missing <{tag}>.")

    parsedate_to_datetime(channel.findtext("lastBuildDate", ""))

    items = channel.findall("item")
    if not items:
        raise ValueError("Feed must contain at least one <item>.")

    previous_date: datetime | None = None
    for item in items:
        for tag in ("title", "link", "guid", "pubDate", "description"):
            if not (item.findtext(tag) or "").strip():
                raise ValueError(f"Item is missing <{tag}>.")

        current_date = parsedate_to_datetime(item.findtext("pubDate", ""))
        if previous_date and current_date > previous_date:
            raise ValueError("Items must be sorted newest first.")
        previous_date = current_date


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="validate and check feed freshness")
    args = parser.parse_args()

    root = Path(__file__).resolve().parents[1]
    feed_path = root / "notes" / "feed.xml"
    generated = generate(root)
    validate_feed(generated)

    if args.check:
        existing = feed_path.read_text(encoding="utf-8")
        existing_normalized = re.sub(
            r"<lastBuildDate>.*?</lastBuildDate>",
            "<lastBuildDate></lastBuildDate>",
            existing,
            flags=re.DOTALL,
        )
        generated_normalized = re.sub(
            r"<lastBuildDate>.*?</lastBuildDate>",
            "<lastBuildDate></lastBuildDate>",
            generated,
            flags=re.DOTALL,
        )
        if existing_normalized != generated_normalized:
            print(f"{feed_path} is out of date. Run python3 scripts/generate_notes_feed.py.", file=sys.stderr)
            return 1
        validate_feed(existing)
        print(f"{feed_path} is valid RSS 2.0.")
        return 0

    feed_path.write_text(generated, encoding="utf-8")
    print(f"Wrote {feed_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

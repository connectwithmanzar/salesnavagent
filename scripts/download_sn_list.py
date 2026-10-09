#!/usr/bin/env python3
"""Download a LinkedIn Sales Navigator people list using a local browser session."""

from __future__ import annotations

import argparse
import json
import re
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

from excel import write_files
from parse import company_mix, list_id, page_url

try:
    from playwright.sync_api import sync_playwright
except ImportError:
    sync_playwright = None

JS_PATH = HERE / "extract_list_page.js"
DEFAULT_PROFILE = Path.home() / ".salesnavagent" / "chrome-profile"
DEFAULT_OUT = Path.home() / "Downloads"
EXTRACT_JS = JS_PATH.read_text(encoding="utf-8")
LOGIN_WAIT_S = 180
PAGE_ATTEMPTS = 8
LOGIN_RE = re.compile(r"authwall|signup|/login|checkpoint", re.I)


def die_missing_playwright() -> None:
    raise SystemExit(
        "Playwright is not installed. From the salesnavagent folder run:\n"
        "  python3 -m pip install -r requirements.txt\n"
        "  python3 -m playwright install chromium"
    )


def launch_context(playwright, profile: Path):
    profile.mkdir(parents=True, exist_ok=True)
    options = {
        "user_data_dir": str(profile),
        "headless": False,
        "viewport": {"width": 1440, "height": 900},
        "ignore_default_args": ["--enable-automation"],
        "args": ["--disable-blink-features=AutomationControlled"],
    }
    try:
        return playwright.chromium.launch_persistent_context(channel="chrome", **options)
    except Exception:
        return playwright.chromium.launch_persistent_context(**options)


def extract(page) -> dict:
    raw = page.evaluate(EXTRACT_JS)
    if isinstance(raw, str):
        try:
            return json.loads(raw)
        except json.JSONDecodeError:
            return {}
    return raw or {}


def on_login_wall(page, data: dict) -> bool:
    if data.get("blocked"):
        return True
    href = (page.url or "") + " " + (page.title() or "")
    return bool(LOGIN_RE.search(href))


def wait_for_login(page) -> None:
    print(
        f"Sales Navigator login required. Sign in in the opened browser. Waiting {LOGIN_WAIT_S}s…",
        flush=True,
    )
    deadline = time.time() + LOGIN_WAIT_S
    while time.time() < deadline:
        time.sleep(2.5)
        data = extract(page)
        if not on_login_wall(page, data):
            print("Login detected. Continuing.", flush=True)
            return
    raise SystemExit("Still on the LinkedIn login screen. Sign in and run the command again.")


def scrape_page(page, url: str, n: int) -> dict:
    page.goto(page_url(url, n), wait_until="domcontentloaded")
    last: dict = {}
    first_wait = 4.0 if n == 1 else 5.0
    for attempt in range(PAGE_ATTEMPTS):
        time.sleep(first_wait if attempt == 0 else 1.5)
        data = extract(page)
        if data:
            last = data
        if data.get("blocked"):
            return data
        if data.get("leads"):
            return data
        if data.get("listName") and attempt >= 4:
            return data
    return last


def collect_leads(page, url: str) -> tuple[list[dict], str, int]:
    all_leads: list[dict] = []
    seen: set[str] = set()
    list_name = ""
    total_hint = 0
    empty = 0
    for page_n in range(1, 41):
        print(f"page {page_n}...", flush=True)
        data = scrape_page(page, url, page_n)
        if on_login_wall(page, data):
            wait_for_login(page)
            data = scrape_page(page, url, page_n)
            if on_login_wall(page, data):
                raise SystemExit("LinkedIn login wall. Sign into Sales Navigator in the browser and retry.")
        if data.get("listName"):
            list_name = data["listName"]
        if data.get("total"):
            total_hint = int(data["total"])
        leads = data.get("leads") or []
        print(f"  {len(leads)} rows | list={list_name!r} total={total_hint}", flush=True)
        if not leads:
            empty += 1
            if empty >= 2 or (total_hint and len(all_leads) >= total_hint):
                break
            continue
        empty = 0
        new = 0
        for lead in leads:
            key = (lead.get("linkedin_url") or lead.get("name") or "").lower()
            if not key or key in seen:
                continue
            seen.add(key)
            all_leads.append(lead)
            new += 1
        print(f"  +{new} unique (running {len(all_leads)})", flush=True)
        if total_hint and len(all_leads) >= total_hint:
            break
        if new == 0:
            break
    return all_leads, list_name, total_hint


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Download a LinkedIn Sales Navigator people list to Excel."
    )
    parser.add_argument("url", help="https://www.linkedin.com/sales/lists/people/{id}")
    parser.add_argument(
        "--profile",
        type=Path,
        default=DEFAULT_PROFILE,
        help="Browser profile directory (keeps the LinkedIn login)",
    )
    parser.add_argument(
        "--out",
        type=Path,
        default=DEFAULT_OUT,
        help="Output folder (default: Downloads)",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> None:
    if sync_playwright is None:
        die_missing_playwright()
    args = parse_args(argv)
    url = args.url.strip()
    lid = list_id(url)
    print(f"list {lid}", flush=True)

    with sync_playwright() as playwright:
        context = launch_context(playwright, args.profile)
        page = context.pages[0] if context.pages else context.new_page()
        page.goto(page_url(url, 1), wait_until="domcontentloaded")
        time.sleep(3)
        first = extract(page)
        if on_login_wall(page, first):
            wait_for_login(page)
        try:
            leads, list_name, total_hint = collect_leads(page, url)
        finally:
            context.close()

    if not leads:
        raise SystemExit("No leads extracted. Confirm the list URL and that you are logged into Sales Navigator.")
    out = write_files(leads, list_name, args.out)
    print(f"list={list_name or 'list'} sn_total={total_hint} mix={company_mix(leads)}", flush=True)
    print(str(out), flush=True)


if __name__ == "__main__":
    try:
        main()
    except ValueError as exc:
        raise SystemExit(str(exc)) from exc

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

import chrome_osa
from excel import write_files
from human import CHECKPOINT_RE, browse_like_person, human_pause, rest_between_pages
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
PAGE_ATTEMPTS = 4
LOGIN_RE = re.compile(CHECKPOINT_RE, re.I)


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
        "viewport": {"width": 1280, "height": 800},
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


def on_login_wall(page, data: dict | None = None) -> bool:
    if data and data.get("blocked"):
        return True
    href = (page.url or "") + " " + (page.title() or "")
    if LOGIN_RE.search(href):
        return True
    try:
        text = page.inner_text("body")[:2500]
    except Exception:
        text = ""
    return bool(LOGIN_RE.search(text))


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


def abort_checkpoint() -> None:
    raise SystemExit(
        "LinkedIn asked for a check. Stopped to protect the account. "
        "Wait, use the list in Chrome normally, then retry later. Prefer the Chrome extension."
    )


def scrape_current(page) -> dict:
    browse_like_person(page)
    last: dict = {}
    for attempt in range(PAGE_ATTEMPTS):
        human_pause(5.0, 8.0) if attempt == 0 else human_pause(2.0, 3.5)
        data = extract(page)
        if data:
            last = data
        if on_login_wall(page, data):
            return {"blocked": True, "leads": []}
        if data.get("leads"):
            return data
        if data.get("listName") and attempt >= 2:
            return data
    return last


def fingerprint(page, data: dict) -> str:
    leads = data.get("leads") or []
    first = (leads[0] or {}).get("linkedin_url") if leads else ""
    return f"{page.url}|{first}"


def click_next(page) -> bool:
    selectors = [
        "button[aria-label='Next']",
        "button[aria-label='Next page']",
        "button.artdeco-pagination__button--next",
    ]
    for selector in selectors:
        loc = page.locator(selector)
        if loc.count() and loc.first.is_enabled():
            loc.first.click()
            return True
    return False


def collect_leads(page, url: str) -> tuple[list[dict], str, int]:
    all_leads: list[dict] = []
    seen: set[str] = set()
    seen_prints: set[str] = set()
    list_name = ""
    total_hint = 0
    empty = 0
    page_n = 1
    while page_n <= 40:
        print(f"page {page_n}...", flush=True)
        data = scrape_current(page)
        if on_login_wall(page, data):
            abort_checkpoint()
        mark = fingerprint(page, data)
        if mark in seen_prints and all_leads:
            break
        seen_prints.add(mark)
        if data.get("listName"):
            list_name = data["listName"]
        if data.get("total"):
            total_hint = int(data["total"])
        leads = data.get("leads") or []
        print(f"  {len(leads)} rows | list={list_name!r} total={total_hint}", flush=True)
        if not leads:
            empty += 1
            if empty >= 2:
                break
        else:
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
        rest_between_pages(page_n)
        before = fingerprint(page, data)
        if click_next(page):
            deadline = time.time() + 14
            while time.time() < deadline:
                time.sleep(0.5)
                nxt = extract(page)
                if on_login_wall(page, nxt):
                    abort_checkpoint()
                if fingerprint(page, nxt) != before:
                    break
            else:
                page.goto(page_url(url, page_n + 1), wait_until="domcontentloaded")
        else:
            page.goto(page_url(url, page_n + 1), wait_until="domcontentloaded")
        page_n += 1
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
    parser.add_argument(
        "--engine",
        choices=("chrome", "playwright"),
        default="chrome" if sys.platform == "darwin" else "playwright",
        help="On a Mac, chrome talks to the open Google Chrome tab via Apple Events (fast).",
    )
    return parser.parse_args(argv)


def run_chrome(url: str, out_dir: Path) -> tuple[list[dict], str, int, Path]:
    try:
        leads, list_name, total_hint = chrome_osa.collect_leads(url)
    except RuntimeError as exc:
        message = str(exc)
        if "not allowed" in message.lower() or "(-1743)" in message or "1002" in message:
            raise SystemExit(
                "macOS blocked Apple Events. System Settings → Privacy & Security → Automation: "
                "allow Cursor (or Terminal) to control Google Chrome, then retry."
            ) from exc
        raise SystemExit(message) from exc
    if not leads:
        raise SystemExit("No leads extracted. Keep the people list open in Google Chrome and retry.")
    out = write_files(leads, list_name, out_dir)
    return leads, list_name, total_hint, out


def run_playwright(url: str, out_dir: Path, profile: Path) -> tuple[list[dict], str, int, Path]:
    if sync_playwright is None:
        die_missing_playwright()
    with sync_playwright() as playwright:
        context = launch_context(playwright, profile)
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
    out = write_files(leads, list_name, out_dir)
    return leads, list_name, total_hint, out


def main(argv: list[str] | None = None) -> None:
    args = parse_args(argv)
    url = args.url.strip()
    lid = list_id(url)
    print(f"list {lid} engine={args.engine}", flush=True)
    if args.engine == "chrome":
        if sys.platform != "darwin":
            raise SystemExit("The chrome engine (Apple Events) only runs on macOS. Use --engine playwright.")
        leads, list_name, total_hint, out = run_chrome(url, args.out)
    else:
        leads, list_name, total_hint, out = run_playwright(url, args.out, args.profile)
    print(f"list={list_name or 'list'} sn_total={total_hint} mix={company_mix(leads)}", flush=True)
    print(str(out), flush=True)


if __name__ == "__main__":
    try:
        main()
    except ValueError as exc:
        raise SystemExit(str(exc)) from exc

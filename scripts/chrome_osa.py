"""Talk to the already-open Google Chrome tab via Apple Events (macOS)."""

from __future__ import annotations

import json
import subprocess
import time
from pathlib import Path

from parse import list_id, page_url

HERE = Path(__file__).resolve().parent
LIST_AS = HERE / "list_sales_tabs.applescript"
JS_PATH = HERE / "extract_list_page.js"


def osa(path: Path) -> str:
    result = subprocess.run(["osascript", str(path)], capture_output=True, text=True)
    if result.returncode:
        raise RuntimeError((result.stderr or result.stdout).strip() or "osascript failed")
    return result.stdout.strip()


def osa_source(source: str) -> str:
    result = subprocess.run(["osascript", "-e", source], capture_output=True, text=True)
    if result.returncode:
        raise RuntimeError((result.stderr or result.stdout).strip() or "osascript failed")
    return result.stdout.strip()


def find_tab(lid: str) -> tuple[int, int] | None:
    raw = osa(LIST_AS)
    for line in raw.splitlines():
        if lid in line:
            parts = line.split(",", 3)
            return int(parts[0]), int(parts[1])
    for line in raw.splitlines():
        if "linkedin.com/sales/lists/people" in line:
            parts = line.split(",", 3)
            return int(parts[0]), int(parts[1])
    return None


def ensure_tab(url: str, lid: str) -> tuple[int, int]:
    found = find_tab(lid)
    if found:
        return found
    raw = osa_source(
        """tell application "Google Chrome"
  activate
  tell window 1
    make new tab with properties {URL:"https://www.linkedin.com/sales/home"}
    set idx to count of tabs
  end tell
  return "1," & idx
end tell"""
    )
    win, tab = [int(x) for x in raw.split(",")]
    time.sleep(2)
    nav(win, tab, url)
    time.sleep(2)
    return win, tab


def nav(win: int, tab: int, url: str) -> None:
    quoted = url.replace('"', '\\"')
    osa_source(
        f'tell application "Google Chrome"\n set URL of tab {tab} of window {win} to "{quoted}"\n return "OK"\nend tell'
    )


def extract(win: int, tab: int) -> dict:
    js_path = str(JS_PATH)
    raw = osa_source(
        f'''tell application "Google Chrome"
  set t to tab {tab} of window {win}
  set js to (do shell script "cat " & quoted form of "{js_path}")
  return execute t javascript "(" & js & ")()"
end tell'''
    )
    if not raw or raw == "missing value":
        return {}
    try:
        data = json.loads(raw)
    except json.JSONDecodeError:
        return {}
    return data if isinstance(data, dict) else {}


def scrape_page(win: int, tab: int, url: str, n: int) -> dict:
    nav(win, tab, page_url(url, n))
    last: dict = {}
    wait = 4.0 if n == 1 else 5.0
    for attempt in range(8):
        time.sleep(wait if attempt == 0 else 1.5)
        data = extract(win, tab)
        if data:
            last = data
        if data.get("blocked"):
            return data
        if data.get("leads"):
            return data
        if data.get("listName") and attempt >= 4:
            return data
    return last


def collect_leads(url: str) -> tuple[list[dict], str, int]:
    lid = list_id(url)
    win, tab = ensure_tab(url, lid)
    print(f"Chrome Apple Events window={win} tab={tab} list={lid}", flush=True)
    all_leads: list[dict] = []
    seen: set[str] = set()
    list_name = ""
    total_hint = 0
    empty = 0
    for page in range(1, 41):
        print(f"page {page}...", flush=True)
        data = scrape_page(win, tab, url, page)
        if data.get("blocked"):
            raise SystemExit("LinkedIn login wall. Keep Sales Navigator open in Chrome and retry.")
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

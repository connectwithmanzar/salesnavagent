from __future__ import annotations

import re
from urllib.parse import parse_qs, urlencode, urlparse, urlunparse

LIST_URL_RE = re.compile(r"/sales/lists/people/(\d+)")


def list_id(url: str) -> str:
    m = LIST_URL_RE.search(url or "")
    if not m:
        raise ValueError(
            "URL must be a Sales Navigator people list, like "
            "https://www.linkedin.com/sales/lists/people/{id}"
        )
    return m.group(1)


def page_url(url: str, n: int) -> str:
    parsed = urlparse((url or "").split("#")[0])
    q = parse_qs(parsed.query)
    q["page"] = [str(n)]
    q.setdefault("sortCriteria", ["LAST_ACTIVITY"])
    q.setdefault("sortOrder", ["DESCENDING"])
    return urlunparse(parsed._replace(query=urlencode(q, doseq=True)))


def split_name(full: str) -> tuple[str, str]:
    parts = [p for p in re.split(r"\s+", (full or "").strip()) if p]
    if not parts:
        return "", ""
    if len(parts) == 1:
        return parts[0], ""
    return parts[0], " ".join(parts[1:])


def safe_filename(name: str) -> str:
    cleaned = re.sub(r"[^\w\s\-]+", "", name or "").strip()
    cleaned = re.sub(r"\s+", "_", cleaned) or "SN_people_list"
    return cleaned[:80]


def company_mix(leads: list[dict], limit: int = 8) -> str:
    counts: dict[str, int] = {}
    for lead in leads:
        company = (lead.get("company") or "").strip() or "Unknown"
        counts[company] = counts.get(company, 0) + 1
    top = sorted(counts.items(), key=lambda item: (-item[1], item[0].lower()))[:limit]
    return ", ".join(f"{name} ({n})" for name, n in top)

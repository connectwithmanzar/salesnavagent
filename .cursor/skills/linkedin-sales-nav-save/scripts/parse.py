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


PUBLIC_RE = re.compile(r"(?:https?://(?:www\.)?)?linkedin\.com/in/([^/?#]+)", re.I)
SN_LEAD_RE = re.compile(r"/sales/(?:lead|people)/([^,/?#]+)", re.I)


def to_public_url(raw: str) -> str:
    text = (raw or "").replace("\\u002f", "/").replace("\\/", "/")
    match = PUBLIC_RE.search(text)
    if not match:
        return ""
    slug = match.group(1).strip("/")
    if not slug or slug.lower().startswith("sales") or slug.startswith("ACwAA"):
        return ""
    return f"https://www.linkedin.com/in/{slug}"


def sn_lead_id(raw: str) -> str:
    match = SN_LEAD_RE.search(raw or "")
    return match.group(1) if match else ""


def personal_linkedin_url(raw: str, sn_url: str = "") -> str:
    vanity = to_public_url(raw) or to_public_url(sn_url)
    if vanity:
        return vanity
    lead_id = sn_lead_id(raw) or sn_lead_id(sn_url)
    if lead_id:
        return f"https://www.linkedin.com/in/{lead_id}"
    return ""


def company_mix(leads: list[dict], limit: int = 8) -> str:
    counts: dict[str, int] = {}
    for lead in leads:
        company = (lead.get("company") or "").strip() or "Unknown"
        counts[company] = counts.get(company, 0) + 1
    top = sorted(counts.items(), key=lambda item: (-item[1], item[0].lower()))[:limit]
    return ", ".join(f"{name} ({n})" for name, n in top)


def summarize_export(leads: list[dict], total_hint: int = 0) -> dict:
    vanity = 0
    member_id = 0
    blank = 0
    for lead in leads:
        url = personal_linkedin_url(
            lead.get("linkedin_url") or lead.get("public_url") or "",
            lead.get("sn_url") or "",
        )
        if not url:
            blank += 1
        elif re.search(r"/in/ACwAA", url, re.I):
            member_id += 1
        else:
            vanity += 1
    count = len(leads)
    sn_total = int(total_hint or 0)
    mismatch = bool(sn_total and count != sn_total)
    return {
        "count": count,
        "sn_total": sn_total,
        "vanity": vanity,
        "member_id": member_id,
        "blank": blank,
        "mismatch": mismatch,
        "ok": not blank and not mismatch,
    }


def format_summary(stats: dict, list_name: str = "", mix: str = "") -> str:
    total = f" of {stats['sn_total']}" if stats.get("sn_total") else ""
    lines = [
        f"list={list_name or 'list'} leads={stats['count']}{total}",
        (
            "linkedin URLs: "
            f"vanity={stats['vanity']} member-id={stats['member_id']} blank={stats['blank']}"
        ),
    ]
    if mix:
        lines.append(f"mix={mix}")
    if stats.get("mismatch"):
        lines.append(
            "WARN: extracted count does not match Sales Nav total. Stay on the people list and retry."
        )
    if stats.get("blank"):
        lines.append("WARN: some rows have no LinkedIn URL.")
    return "\n".join(lines)

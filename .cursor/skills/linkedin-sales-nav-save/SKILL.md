---
name: linkedin-sales-nav-save
description: >-
  Downloads a LinkedIn Sales Navigator saved people list (Lead Lists) into Excel
  on the user's Downloads folder. Prefer the Chrome extension. Fall back to the
  local Playwright script only if asked. Use when the user pastes a
  linkedin.com/sales/lists/people URL, asks to download / save / export a Sales
  Nav list, or says "linkedin sales nav save".
---

# LinkedIn Sales Nav save

Download a **saved people list** (`/sales/lists/people/{id}`). Do not use this for people search (`/sales/search/people`).

**Prefer the Chrome extension** for the user's own account. It runs in their real Chrome tab, pages slowly, and does not launch Playwright. Point them at https://connectwithmanzar.github.io/salesnavagent/ unless they explicitly want the CLI.

Never promise the account cannot be restricted. Do not add stealth, fingerprint spoofing, proxies, or extra LinkedIn API calls.

## CLI fallback

```bash
python3 scripts/download_sn_list.py 'https://www.linkedin.com/sales/lists/people/{ID}'
```

The script pages slowly (scroll, click Next, 6–22s between pages) in headed Chrome with no automation-hiding flags. If a checkpoint appears, **stop** and tell the user to wait.

## Output

Writes `~/Downloads/{List_Name}.xlsx` (CLI also writes CSV).

Columns: First Name, Last Name, Full Name, Title, Company, Location, Sales Navigator URL, Date added.

## Gotchas

- Page size is **25**. Use **“N Total results”**, not the first number on the page.
- Click **Next** when possible. Only then fall back to `?page=N`.
- Do not invent leads. Do not visit profiles.

## After download

Reply with the Downloads path, lead count, list name, and a one-line company mix.

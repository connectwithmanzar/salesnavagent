---
name: linkedin-sales-nav-save
description: >-
  Downloads a LinkedIn Sales Navigator saved people list (Lead Lists) into Excel
  on the user's Downloads folder using a local Playwright browser session. Use
  when the user pastes a linkedin.com/sales/lists/people URL, asks to download /
  save / export a Sales Nav list, or says "linkedin sales nav save".
---

# LinkedIn Sales Nav save

Download a **saved people list** (`/sales/lists/people/{id}`). Do not use this for people search (`/sales/search/people`).

This skill runs on any Mac, Windows, or Linux laptop with Cursor Desktop. It is not a cloud agent: LinkedIn login has to happen in a browser on that machine.

## Setup (once per machine)

From the `salesnavagent` repo (or this skill folder's parent repo):

```bash
python3 -m pip install -r requirements.txt
python3 -m playwright install chromium
```

If Google Chrome is installed, the script uses it automatically. LinkedIn login is stored in `~/.salesnavagent/chrome-profile` and reused.

## Run

Resolve the script next to this skill (`scripts/download_sn_list.py`) or at repo `scripts/download_sn_list.py`. Prefer a repo `.venv` if it exists.

```bash
python3 scripts/download_sn_list.py 'https://www.linkedin.com/sales/lists/people/{ID}'
```

Use the URL the user pasted. On first run a browser window opens: tell the user to sign into Sales Navigator there, then wait. Do not scrape with a logged-out fetch.

## Output

Writes `~/Downloads/{List_Name}.xlsx` and `.csv`.

Columns: First Name, Last Name, Full Name, Title, Company, Location, Sales Navigator URL, Date added.

URLs are SN lead links (`/sales/lead/ACwAA…`), not public `/in/` slugs.

## Gotchas (do not “fix” by guessing)

- Typical page size is **25**. A 31-person list is 25 + 6.
- Do **not** trust the first number on the page as the total. Use **“N Total results”**.
- Always paginate with `?page=N`. Wait ~4–5s on first load of each page.
- If the browser shows a login wall, tell the user to sign in in that window and retry. Do not invent leads.
- Excel: Arial, navy header, freeze row 1, autofilter. No extra sheets unless asked.

## After download

Reply with the Downloads path, lead count, list name, and a one-line company mix. Do not recap the scrape mechanics.

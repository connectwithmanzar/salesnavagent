---
name: linkedin-sales-nav-save
description: >-
  Downloads a LinkedIn Sales Navigator saved people list (Lead Lists) into Excel
  on the user's Downloads folder. On a Mac, talk to the already-open Google
  Chrome tab via Apple Events (osascript). Use when the user pastes a
  linkedin.com/sales/lists/people URL, asks to download / save / export a Sales
  Nav list, or says "linkedin sales nav save".
---

# LinkedIn Sales Nav save

Download a **saved people list** (`/sales/lists/people/{id}`). Do not use this for people search. Do not write a new scraper. Do not visit individual profiles.

## Which path

- **macOS:** keep the list open in **Google Chrome** (already logged into Sales Navigator). Run the command below (Apple Events).
- **Anyone else, or teammates:** Chrome extension at https://connectwithmanzar.github.io/salesnavagent/ — Load unpacked, navy card must say **v1.5.1**. Chrome Safety Check may warn because it is not on the Chrome Web Store; that is expected.

```bash
python3 scripts/download_sn_list.py 'https://www.linkedin.com/sales/lists/people/{ID}'
```

Wait ~4s on page 1 and ~5s on later pages so Sales Nav can render. Do not add extra “human” delays. If macOS asks, allow Cursor/Terminal to control Google Chrome (System Settings → Privacy & Security → Automation).

## After a successful run

Read the script summary and reply with:

- Excel path
- lead count vs Sales Nav total (`leads=N of T`)
- LinkedIn URL mix: vanity vs member-id (`/in/ACwAA…`) vs blank
- list name and a one-line company mix

If count does not match Sales Nav total, say the export is incomplete and stay on the list to retry. If any LinkedIn URL is blank, say so. Member-id URLs still open the profile; do not visit pages to hunt vanity slugs.

Search URLs (`/sales/search/people`) are invalid — refuse them.

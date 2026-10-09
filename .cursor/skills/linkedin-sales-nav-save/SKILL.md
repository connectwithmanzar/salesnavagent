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

Download a **saved people list** (`/sales/lists/people/{id}`). Do not use this for people search.

On **macOS**, keep the list open in **Google Chrome** (user already logged into Sales Navigator). Run:

```bash
python3 scripts/download_sn_list.py 'https://www.linkedin.com/sales/lists/people/{ID}'
```

That is the fast path we used before: Apple Events (`osascript`) set the tab URL to `?page=N` and `execute javascript` on that tab. Wait ~4s on page 1 and ~5s on later pages so Sales Nav can render. Do not add extra “human” delays.

If macOS asks, allow Cursor/Terminal to control Google Chrome (System Settings → Privacy & Security → Automation). That is Apple Events, not Chrome Developer mode.

Teammates on any laptop can use the Chrome extension: https://connectwithmanzar.github.io/salesnavagent/

## Output

`~/Downloads/{List_Name}.xlsx`. Reply with path, lead count, list name, and a one-line company mix.

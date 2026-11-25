# Sales Nav List Save

Teammates download a LinkedIn Sales Navigator **people list** to Excel from Chrome. No Cursor, no terminal.

**Install link:** [https://connectwithmanzar.github.io/salesnavagent/](https://connectwithmanzar.github.io/salesnavagent/)

1. Open that page and download the zip (version **1.5.1**).
2. Unzip, then in Chrome go to `chrome://extensions`, turn on **Developer mode**, **Load unpacked**, and pick the `salesnav-list-save` folder. Confirm the navy card says **v1.5.1**.
3. Open a saved people list. Click **Download Excel**. The file lands in Downloads with `linkedin.com/in/` profile URLs. It stays on the list page — Cancel stops immediately.

It is an internal unpacked tool, not a Chrome Web Store listing. Chrome Safety Check may warn about that; it does not mean the export is broken. If you already had an older copy, **Remove** it, then Load unpacked again — Reload on an old Downloads folder will not pick this up.

It only works on saved people lists (`/sales/lists/people/{id}`), not search results. It does not visit each profile. List data stays on the computer.

## Cursor / CLI on a Mac (fast path)

Keep the people list open in Google Chrome (already logged into Sales Navigator). Then:

```bash
python3 scripts/download_sn_list.py 'https://www.linkedin.com/sales/lists/people/{ID}'
```

That uses Apple Events (`osascript`) on the Chrome tab you already have — the same method as before. Wait is only ~4–5s per page so the list can render. If macOS asks, allow Cursor/Terminal to control Google Chrome under System Settings → Privacy & Security → Automation.

```bash
python3 -m unittest discover -s tests
```

# Sales Nav List Save

Teammates download a LinkedIn Sales Navigator **people list** to Excel from Chrome. No Cursor, no terminal.

**Install link:** [https://connectwithmanzar.github.io/salesnavagent/](https://connectwithmanzar.github.io/salesnavagent/)

1. Open that page and click **Download for Chrome**.
2. Unzip, then in Chrome go to `chrome://extensions`, turn on **Developer mode**, **Load unpacked**, and pick the `salesnav-list-save` folder.
3. Open a saved people list. Click **Download Excel**. The file lands in Downloads.

It only works on saved people lists (`/sales/lists/people/{id}`), not search results. It runs in your real Chrome session, scrolls and clicks Next with human-like pauses, and stops if LinkedIn shows a checkpoint. Nothing can make LinkedIn “unbannable”; this is the lowest-risk design because it is not a second automated browser.

If the extension is already installed, click **Reload** on `chrome://extensions` after updating.

## Cursor / CLI on a Mac (fast path)

Keep the people list open in Google Chrome (already logged into Sales Navigator). Then:

```bash
python3 scripts/download_sn_list.py 'https://www.linkedin.com/sales/lists/people/{ID}'
```

That uses Apple Events (`osascript`) on the Chrome tab you already have — the same method as before. Wait is only ~4–5s per page so the list can render. If macOS asks, allow Cursor/Terminal to control Google Chrome under System Settings → Privacy & Security → Automation.

```bash
python3 -m unittest discover -s tests
```

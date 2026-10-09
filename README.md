# salesnavagent

Cursor agent that downloads a LinkedIn Sales Navigator **people list** to Excel.

Paste a list URL in a Cursor chat in this repo, or run the command below. Works on Mac, Windows, and Linux. LinkedIn login happens once in a local browser and is reused.

## Use in Cursor (any laptop)

1. Install [Cursor](https://cursor.com).
2. Clone and open this folder:

```bash
git clone https://github.com/connectwithmanzar/salesnavagent.git
cd salesnavagent
```

3. One-time setup:

```bash
python3 -m venv .venv
# Mac/Linux:
source .venv/bin/activate
# Windows: .venv\Scripts\activate
python -m pip install -r requirements.txt
python -m playwright install chromium
```

4. In Cursor: **File → Open Folder** on `salesnavagent`, start a new chat, paste a URL like:

`https://www.linkedin.com/sales/lists/people/7514252219261751296`

The first run opens a browser. Sign into Sales Navigator there. Later runs reuse `~/.salesnavagent/chrome-profile`.

## Use from the terminal

```bash
python3 scripts/download_sn_list.py 'https://www.linkedin.com/sales/lists/people/{ID}'
```

Excel and CSV land in your Downloads folder.

## Use in any Cursor chat on this Mac

The `linkedin-sales-nav-save` skill is also in your personal Cursor Agent Store. In a new chat in any project, paste a Sales Nav people-list URL (or say “linkedin sales nav save”).

On another laptop, clone this repo and open it in Cursor so the project skill is available. Copy `.cursor/skills/linkedin-sales-nav-save/` into that machine’s Agent Store if you want the same skill in every project.

## Limits

- Saved **people lists** only (`/sales/lists/people/{id}`), not search results.
- Must run on the laptop (Cursor Desktop). A cloud agent cannot use your LinkedIn session.
- Google Chrome is used when installed; otherwise Playwright Chromium.

## Tests

```bash
python3 -m unittest discover -s tests
```

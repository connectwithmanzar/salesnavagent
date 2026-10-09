# Sales Nav List Save

Teammates download a LinkedIn Sales Navigator **people list** to Excel from Chrome. No Cursor, no terminal.

**Install link:** [https://connectwithmanzar.github.io/salesnavagent/](https://connectwithmanzar.github.io/salesnavagent/)

1. Open that page and click **Download for Chrome**.
2. Unzip, then in Chrome go to `chrome://extensions`, turn on **Developer mode**, **Load unpacked**, and pick the `salesnav-list-save` folder.
3. Open a saved people list. Click **Download Excel**. The file lands in Downloads.

It only works on saved people lists (`/sales/lists/people/{id}`), not search results. Chrome uses the Sales Navigator login already in the browser.

## Cursor / CLI (optional)

For local agent use, clone this repo, run `./install.sh`, and either paste a list URL in Cursor or:

```bash
python3 scripts/download_sn_list.py 'https://www.linkedin.com/sales/lists/people/{ID}'
```

```bash
python3 -m unittest discover -s tests
```

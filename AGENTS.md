# salesnavagent

Product for SDRs: Chrome extension that downloads LinkedIn Sales Navigator saved people lists to Excel.

- Teammate install page: `docs/` (GitHub Pages)
- Extension source: `extension/`
- Pack zip: `scripts/pack_extension.sh` writes `docs/salesnav-list-save.zip`
- Cursor/CLI fallback: `.cursor/skills/linkedin-sales-nav-save/SKILL.md` and `python3 scripts/download_sn_list.py '<list-url>'`

The extension must stay in the user's real Chrome session. Page slowly (scroll, click Next, random pauses). Stop on checkpoint. Do not add stealth, fingerprint spoofing, or LinkedIn API scraping.

Do not point teammates at Python or Cursor unless they ask. Saved people lists only (`/sales/lists/people/{id}`).

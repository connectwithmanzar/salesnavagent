# salesnavagent

Product for SDRs: Chrome extension that downloads LinkedIn Sales Navigator saved people lists to Excel.

- Teammate install page: `docs/` (GitHub Pages)
- Extension source: `extension/`
- Pack zip: `scripts/pack_extension.sh` writes `docs/salesnav-list-save.zip`
- Cursor/CLI fallback: `.cursor/skills/linkedin-sales-nav-save/SKILL.md` and `python3 scripts/download_sn_list.py '<list-url>'`

The extension must stay in the user's real Chrome session. Stay on the people-list page. Do not visit each lead profile. Do not inject MAIN-world scripts or hook `fetch` / XHR. Cancel must stop immediately. Do not add stealth, fingerprint spoofing, or extra LinkedIn API calls. Reading profile ids already present on the list page is allowed.

Keep host permissions limited to `/sales/lists/people/*`. Do not market the zip as “Download for Chrome” (that looks like unofficial Web Store distribution and trips Google Safe Browsing). Chrome Safety Check warnings on unpacked team tools are expected.

Do not point teammates at Python or Cursor unless they ask. Saved people lists only (`/sales/lists/people/{id}`).

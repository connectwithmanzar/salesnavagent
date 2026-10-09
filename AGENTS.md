# salesnavagent

Cursor agent for downloading LinkedIn Sales Navigator saved people lists to Excel.

- Skill: `.cursor/skills/linkedin-sales-nav-save/SKILL.md`
- Command: `python3 scripts/download_sn_list.py '<list-url>'`
- First run on a machine: `python3 -m pip install -r requirements.txt` then `python3 -m playwright install chromium`. A browser window opens; the user signs into Sales Navigator once. Login is reused from `~/.salesnavagent/chrome-profile`.
- Works in Cursor Desktop on Mac, Windows, and Linux. Does not run as a cloud-only agent (no access to the user's LinkedIn session).

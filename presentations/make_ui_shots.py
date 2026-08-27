#!/usr/bin/env python3
"""Instructional UI screenshots for the 5-slide playbook."""

from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

OUT = Path("/Users/manzar.i/Desktop/sdr-data-consolidator/presentations/assets")
SMALL = ImageFont.truetype("/System/Library/Fonts/Supplemental/Arial.ttf", 16)
SMALLB = ImageFont.truetype("/System/Library/Fonts/Supplemental/Arial Bold.ttf", 16)
TINY = ImageFont.truetype("/System/Library/Fonts/Supplemental/Arial.ttf", 13)
TINYB = ImageFont.truetype("/System/Library/Fonts/Supplemental/Arial Bold.ttf", 13)
H1 = ImageFont.truetype("/System/Library/Fonts/Supplemental/Arial Bold.ttf", 28)
H2 = ImageFont.truetype("/System/Library/Fonts/Supplemental/Arial Bold.ttf", 20)

BLUE = (0, 86, 240)
INK = (16, 32, 55)
MUTED = (90, 108, 128)
LINE = (220, 228, 236)
WHITE = (255, 255, 255)


def rr(draw, xy, r, fill, outline=None, width=1):
    draw.rounded_rectangle(xy, radius=r, fill=fill, outline=outline, width=width)


def chrome_chrome(draw, w, title):
    rr(draw, (20, 16, w - 20, 70), 10, (232, 234, 237))
    for i, c in enumerate([(255, 95, 86), (255, 189, 46), (39, 201, 63)]):
        draw.ellipse((36 + i * 22, 32, 52 + i * 22, 48), fill=c)
    rr(draw, (130, 28, w - 40, 58), 8, WHITE, (210, 214, 220), 1)
    draw.text((146, 34), title, font=TINY, fill=MUTED)


def shot_sn_list():
    w, h = 1400, 820
    im = Image.new("RGB", (w, h), (232, 234, 237))
    d = ImageDraw.Draw(im)
    chrome_chrome(d, w, "linkedin.com/sales/lists/people/…   ·   SIMILAR MERCHENT V2")
    rr(d, (20, 80, w - 20, h - 20), 12, WHITE)
    d.rectangle((20, 80, 280, h - 20), fill=(247, 249, 251))
    nav = ["Home", "Accounts", "Leads", "Lead lists", "Messaging"]
    for i, name in enumerate(nav):
        y = 120 + i * 48
        if name == "Lead lists":
            rr(d, (36, y - 8, 264, y + 32), 8, (232, 240, 255))
            d.text((52, y), name, font=SMALLB, fill=BLUE)
        else:
            d.text((52, y), name, font=SMALL, fill=INK)
    d.text((310, 110), "SIMILAR MERCHENT V2", font=H1, fill=INK)
    d.text((310, 155), "Lead list", font=SMALL, fill=MUTED)
    rr(d, (310, 200, 520, 248), 8, (232, 240, 255))
    d.text((328, 212), "49  Total results", font=SMALLB, fill=BLUE)
    d.rectangle((310, 280, w - 48, 320), fill=(247, 249, 251))
    for x, lab in ((330, "Name"), (620, "Title"), (980, "Company")):
        d.text((x, 290), lab, font=TINYB, fill=MUTED)
    rows = [
        ("Marina Mitterbucher", "Online Marketing Managerin", "skapetze"),
        ("Verena Skapetze", "Marketingleitung", "skapetze"),
        ("Jean-Baptiste R.", "Senior Performance Marketing", "moebel.de"),
        ("…", "25 people per page", "page 1 of 2"),
    ]
    for i, (n, t, c) in enumerate(rows):
        y = 340 + i * 52
        d.line((310, y + 44, w - 48, y + 44), fill=LINE)
        d.text((330, y), n, font=SMALLB, fill=INK)
        d.text((620, y), t, font=SMALL, fill=INK)
        d.text((980, y), c, font=SMALL, fill=MUTED)
    rr(d, (980, 188, w - 48, 268), 10, (255, 247, 230), (232, 170, 70), 2)
    d.text((996, 204), "Check these two things", font=TINYB, fill=(150, 90, 10))
    d.text((996, 228), "List name  +  Total results", font=SMALLB, fill=INK)
    im.save(OUT / "shot_sn_list.png", optimize=True)


def shot_chrome_menu():
    w, h = 1400, 720
    im = Image.new("RGB", (w, h), (236, 239, 243))
    d = ImageDraw.Draw(im)
    d.text((40, 24), "Top of the Mac screen  —  not inside Chrome Settings", font=SMALL, fill=MUTED)
    d.rectangle((0, 70, w, 118), fill=(246, 246, 248))
    d.line((0, 118, w, 118), fill=(210, 212, 216))
    items = [("Chrome", 40), ("File", 160), ("Edit", 240), ("View", 330), ("History", 430), ("Bookmarks", 540)]
    for name, x in items:
        if name == "View":
            d.rectangle((318, 74, 400, 114), fill=BLUE)
            d.text((x, 82), name, font=SMALLB, fill=WHITE)
        else:
            d.text((x, 82), name, font=SMALL, fill=INK)
    rr(d, (318, 126, 620, 430), 10, WHITE, (210, 214, 220), 1)
    view_items = ["Stop", "Reload This Page", "Font", "Developer  ›"]
    for i, name in enumerate(view_items):
        y = 148 + i * 44
        if "Developer" in name:
            d.rectangle((328, y - 8, 610, y + 32), fill=(232, 240, 255))
            d.text((348, y), name, font=SMALLB, fill=BLUE)
        else:
            d.text((348, y), name, font=SMALL, fill=INK)
    rr(d, (628, 250, 1180, 520), 10, WHITE, (210, 214, 220), 1)
    sub = [
        ("View Source", False),
        ("Developer Tools", False),
        ("JavaScript Console", False),
        ("Allow JavaScript from Apple Events    ✓", True),
        ("Task Manager", False),
    ]
    for i, (name, on) in enumerate(sub):
        y = 278 + i * 42
        if on:
            d.rectangle((640, y - 10, 1168, y + 30), fill=BLUE)
            d.text((660, y), name, font=SMALLB, fill=WHITE)
        else:
            d.text((660, y), name, font=SMALL, fill=INK)
    rr(d, (40, 560, 1360, 680), 12, WHITE, BLUE, 2)
    d.text((64, 582), "Click View  (next to Edit).  Then Developer.  Then this line until a tick appears.", font=SMALLB, fill=INK)
    d.text((64, 622), "If you land on a gear / Settings page, you are in the wrong place.", font=SMALL, fill=MUTED)
    im.save(OUT / "shot_chrome_menu.png", optimize=True)


def shot_cursor_agent():
    w, h = 1200, 640
    im = Image.new("RGB", (w, h), (18, 22, 28))
    d = ImageDraw.Draw(im)
    rr(d, (24, 24, w - 24, h - 24), 16, (28, 32, 40))
    d.text((48, 48), "Cursor", font=SMALLB, fill=(180, 190, 205))
    d.text((48, 88), "New Chat", font=H2, fill=WHITE)
    d.text((48, 130), "Mode must be Agent. Ask can only talk. Agent can export the list.", font=SMALL, fill=(150, 162, 180))
    rr(d, (48, 200, w - 48, 430), 14, (40, 45, 54), (70, 78, 92), 1)
    d.text((72, 224), "Export the open Sales Navigator lead list to CSV. Save it in Downloads.", font=SMALL, fill=WHITE)
    rr(d, (72, 340, 170, 384), 8, (50, 55, 64))
    d.text((96, 350), "Ask", font=SMALL, fill=(160, 168, 180))
    rr(d, (186, 340, 310, 384), 8, BLUE)
    d.text((214, 350), "Agent", font=SMALLB, fill=WHITE)
    rr(d, (326, 340, 430, 384), 8, (50, 55, 64))
    d.text((348, 350), "Plan", font=SMALL, fill=(160, 168, 180))
    d.text((72, 470), "Cmd + I   opens chat", font=TINY, fill=(130, 140, 155))
    rr(d, (48, 520, w - 48, 590), 10, (20, 70, 50))
    d.text((72, 542), "Look for Agent highlighted in blue before you press Return.", font=SMALLB, fill=(140, 230, 180))
    im.save(OUT / "shot_cursor_agent.png", optimize=True)


def shot_downloads():
    w, h = 1200, 560
    im = Image.new("RGB", (w, h), (236, 239, 243))
    d = ImageDraw.Draw(im)
    rr(d, (30, 30, w - 30, h - 30), 14, WHITE)
    d.rectangle((30, 30, w - 30, 86), fill=(247, 249, 251))
    d.text((52, 48), "Finder   ›   Downloads", font=SMALLB, fill=INK)
    for x, lab in ((52, "Name"), (620, "Date"), (900, "Kind")):
        d.text((x, 110), lab, font=TINYB, fill=MUTED)
    d.line((52, 140, w - 52, 140), fill=LINE)
    files = [
        ("Similar_Merchent_V2_prospects.csv", "Today", "CSV", True),
        ("Nicole_2_prospects.csv", "20 Aug", "CSV", False),
        ("Taboola_SN_Export_Playbook.pptx", "Today", "PowerPoint", False),
    ]
    for i, (name, date, kind, on) in enumerate(files):
        y = 160 + i * 70
        if on:
            rr(d, (44, y - 12, w - 48, y + 48), 8, (232, 240, 255))
        d.text((52, y), name, font=SMALLB, fill=BLUE if on else INK)
        d.text((620, y), date, font=SMALL, fill=MUTED)
        d.text((900, y), kind, font=SMALL, fill=MUTED)
    rr(d, (44, 400, w - 48, 500), 10, (255, 247, 230), (232, 170, 70), 2)
    d.text((64, 422), "Open the CSV. Count the rows.", font=SMALLB, fill=INK)
    d.text((64, 456), "If the list said 49 Total results, the sheet should have 49 people.", font=SMALL, fill=MUTED)
    im.save(OUT / "shot_downloads.png", optimize=True)


def shot_cursor_install():
    w, h = 720, 420
    im = Image.new("RGB", (w, h), (18, 22, 28))
    d = ImageDraw.Draw(im)
    rr(d, (24, 24, w - 24, h - 24), 16, (28, 32, 40))
    d.rounded_rectangle((48, 48, 120, 120), 16, fill=BLUE)
    d.text((68, 68), "C", font=H1, fill=WHITE)
    d.text((144, 62), "Cursor", font=H2, fill=WHITE)
    d.text((144, 96), "cursor.com  ·  Mac app", font=SMALL, fill=(150, 162, 180))
    d.text((48, 160), "1. Download Cursor", font=SMALLB, fill=WHITE)
    d.text((48, 210), "2. Sign in with your Taboola email", font=SMALLB, fill=WHITE)
    d.text((48, 260), "3. You do not need a code folder", font=SMALLB, fill=WHITE)
    im.save(OUT / "shot_cursor_install.png", optimize=True)


if __name__ == "__main__":
    OUT.mkdir(exist_ok=True)
    shot_sn_list()
    shot_chrome_menu()
    shot_cursor_agent()
    shot_downloads()
    shot_cursor_install()
    print("ok")

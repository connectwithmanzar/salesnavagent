from __future__ import annotations

import random
import time

CHECKPOINT_RE = (
    r"authwall|signup|checkpoint|captcha|/login|/challenge|"
    r"unusual activity|verify your identity|security challenge|restricted account"
)


def human_pause(min_s: float, max_s: float) -> None:
    time.sleep(random.uniform(min_s, max_s))


def rest_between_pages(page_count: int) -> None:
    if page_count > 0 and page_count % 4 == 0:
        human_pause(12.0, 22.0)
    else:
        human_pause(6.0, 11.0)


def browse_like_person(page) -> None:
    for _ in range(random.randint(2, 4)):
        page.mouse.wheel(0, random.randint(180, 400))
        human_pause(0.45, 0.95)
    page.evaluate("window.scrollTo({ top: 0, behavior: 'smooth' })")
    human_pause(0.4, 0.9)

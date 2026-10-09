function randBetween(min, max) {
  return min + Math.random() * (max - min);
}

function sleep(ms) {
  return new Promise((resolve) => setTimeout(resolve, ms));
}

function pageLooksRestricted() {
  const loc = `${location.href} ${document.title}`;
  if (/authwall|signup|checkpoint|captcha|\/login|\/challenge/i.test(loc)) return true;
  const text = (document.body?.innerText || "").slice(0, 2500);
  return /unusual activity|verify your identity|security challenge|restricted account|try again later/i.test(
    text
  );
}

async function waitUntilTabVisible() {
  while (document.hidden) {
    await new Promise((resolve) => {
      document.addEventListener("visibilitychange", resolve, { once: true });
    });
  }
}

async function humanPause(minMs, maxMs) {
  await waitUntilTabVisible();
  await sleep(randBetween(minMs, maxMs));
}

async function browseListLikeAPerson() {
  await waitUntilTabVisible();
  const table = document.querySelector("table") || document.scrollingElement || document.body;
  const steps = 2 + Math.floor(Math.random() * 3);
  for (let i = 0; i < steps; i += 1) {
    table.scrollBy({ top: randBetween(160, 380), behavior: "smooth" });
    await sleep(randBetween(450, 950));
  }
  table.scrollTo({ top: 0, behavior: "smooth" });
  await sleep(randBetween(400, 900));
}

function findNextButton() {
  const nodes = Array.from(document.querySelectorAll("button, a"));
  return (
    nodes.find((el) => {
      if (el.disabled || el.getAttribute("aria-disabled") === "true") return false;
      const label = (el.getAttribute("aria-label") || "").trim();
      return /^(next|next page)$/i.test(label);
    }) ||
    nodes.find((el) => {
      if (el.disabled || el.getAttribute("aria-disabled") === "true") return false;
      const text = (el.textContent || "").replace(/\s+/g, " ").trim();
      return /^(next|next page)$/i.test(text);
    }) ||
    null
  );
}

function listFingerprint() {
  const lead =
    document.querySelector("a.lists-detail__view-profile-name-link, a[href*='/sales/lead/']") ||
    null;
  return `${location.href}|${(lead && (lead.getAttribute("href") || lead.textContent)) || ""}`;
}

async function goToNextListPage() {
  const before = listFingerprint();
  const next = findNextButton();
  if (next) {
    next.click();
    const deadline = Date.now() + 14000;
    while (Date.now() < deadline) {
      await sleep(400);
      if (pageLooksRestricted()) return "restricted";
      if (listFingerprint() !== before) return "clicked";
    }
  }
  return "fallback";
}

() => {
  function toPublic(raw) {
    const text = String(raw || "").replace(/\\u002f/gi, "/").replace(/\\\//g, "/");
    const match = text.match(/(?:https?:\/\/(?:www\.)?)?linkedin\.com\/in\/([^/?#"'\s]+)/i);
    if (!match) return "";
    const slug = match[1].replace(/\/$/, "");
    if (!slug || /^sales/i.test(slug) || slug.startsWith("ACwAA")) return "";
    return "https://www.linkedin.com/in/" + slug;
  }

  function findViewLink() {
    const link = Array.from(document.querySelectorAll("a[href]")).find((el) => {
      const label = (el.innerText || "").replace(/\s+/g, " ").trim();
      const href = el.getAttribute("href") || el.href || "";
      return /\/in\//i.test(href) && (/view linkedin profile/i.test(label) || /linkedin\.com\/in\//i.test(href));
    });
    return link ? toPublic(link.href || link.getAttribute("href") || "") : "";
  }

  document.querySelectorAll('button[aria-label="Dismiss"]').forEach((el) => {
    try {
      el.click();
    } catch (err) {}
  });

  let url = findViewLink() || toPublic(document.documentElement.innerHTML);
  if (!url) {
    const overflow = Array.from(document.querySelectorAll("button")).find((el) =>
      /open actions overflow menu|more actions/i.test(el.getAttribute("aria-label") || "")
    );
    if (overflow) {
      try {
        overflow.click();
      } catch (err) {}
    }
    url = findViewLink();
  }

  const html = document.documentElement.innerHTML || "";
  if (!url) {
    const flag = html.match(/flagshipProfileUrl"\s*:\s*"([^"]+)"/i);
    if (flag) url = toPublic(flag[1]);
  }
  if (!url) {
    const ident = html.match(/publicIdentifier"\s*:\s*"([^"]+)"/i);
    if (ident && !/^ACwAA/i.test(ident[1])) url = "https://www.linkedin.com/in/" + ident[1].replace(/\\u002d/gi, "-");
  }

  return JSON.stringify({
    href: location.href,
    title: document.title,
    public_url: url,
  });
}

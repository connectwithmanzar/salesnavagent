() => {
  const href = location.href || "";
  const title = document.title || "";
  const text = (document.body?.innerText || "").replace(/\u00a0/g, " ");
  const blocked =
    /authwall|signup|checkpoint|captcha|\/login|\/challenge/i.test(`${href} ${title}`) ||
    /unusual activity|verify your identity|security challenge|restricted account/i.test(
      text.slice(0, 2500)
    );
  const lines = text
    .split("\n")
    .map((line) => line.replace(/\s+/g, " ").trim())
    .filter(Boolean);

  let listName = title.replace(/\s*\|\s*Sales Navigator.*$/i, "").trim();
  const h1 = document.querySelector("h1");
  if (h1 && (h1.innerText || "").trim()) {
    listName = (h1.innerText || "").replace(/\s+/g, " ").trim();
  }
  const named = lines.findIndex((line) => /^lead lists$/i.test(line));
  if (named >= 0 && lines[named + 1] && !/view in search|copy list|share list/i.test(lines[named + 1])) {
    listName = lines[named + 1];
  }

  let total = 0;
  let page = 1;
  const pageM = href.match(/[?&]page=(\d+)/i);
  if (pageM) page = parseInt(pageM[1], 10);
  const totalM = text.match(/(\d[\d,]*)\s+Total results/i);
  if (totalM) total = parseInt(totalM[1].replace(/,/g, ""), 10);
  if (!total) {
    const ofM =
      text.match(/Showing\s+\d[\d,]*\s*[–-]\s*\d[\d,]*\s+of\s+(\d[\d,]*)/i) ||
      text.match(/(\d[\d,]*)\s+of\s+(\d[\d,]*)\s+results/i);
    if (ofM) total = parseInt((ofM[ofM.length - 1] || "").replace(/,/g, ""), 10);
  }

  const leads = [];
  const seen = new Set();

  function push(name, titleText, company, location, hrefLead, extra) {
    name = (name || "").replace(/\s+/g, " ").trim();
    if (!name || name.length < 2) return;
    hrefLead = (hrefLead || "").split("?")[0];
    if (hrefLead.startsWith("/")) hrefLead = "https://www.linkedin.com" + hrefLead;
    const key = hrefLead || name.toLowerCase();
    if (seen.has(key)) return;
    seen.add(key);
    leads.push({
      name,
      title: (titleText || "").replace(/\s+/g, " ").trim(),
      company: (company || "").replace(/\s+/g, " ").trim(),
      location: (location || "").replace(/\s+/g, " ").trim(),
      linkedin_url: hrefLead,
      extra: extra || "",
    });
  }

  for (const tr of document.querySelectorAll("table tbody tr")) {
    const nameA =
      tr.querySelector("a.lists-detail__view-profile-name-link") ||
      tr.querySelector('a[href*="/sales/lead/"]') ||
      tr.querySelector('a[href*="/sales/people/"]') ||
      tr.querySelector("a[data-anonymize='person-name']");
    if (!nameA) continue;
    const tds = Array.from(tr.querySelectorAll("td")).map((td) =>
      (td.innerText || "").replace(/\s+/g, " ").trim()
    );
    let dateAdded = "";
    for (const td of tds) {
      if (/^\d{1,2}\/\d{1,2}\/\d{4}$/.test(td)) dateAdded = td;
    }
    push(
      nameA.innerText,
      tr.querySelector('[data-anonymize="job-title"]')?.innerText || "",
      tr.querySelector('[data-anonymize="company-name"]')?.innerText || "",
      tr.querySelector('[data-anonymize="location"]')?.innerText || "",
      nameA.getAttribute("href") || "",
      dateAdded
    );
  }

  if (!leads.length) {
    for (const a of document.querySelectorAll('a[href*="/sales/lead/"], a[href*="/sales/people/"]')) {
      const card = a.closest("li, article, tr, div") || a.parentElement;
      const blob = (card?.innerText || "")
        .split("\n")
        .map((line) => line.replace(/\s+/g, " ").trim())
        .filter(Boolean);
      push(
        a.innerText || blob[0],
        blob[1] || "",
        blob[2] || "",
        blob[3] || "",
        a.getAttribute("href") || "",
        ""
      );
    }
  }

  return JSON.stringify({
    href,
    title,
    listName,
    blocked,
    page,
    total,
    count: leads.length,
    sample: lines.slice(0, 30),
    leads,
  });
}

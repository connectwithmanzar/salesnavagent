function extractListPage() {
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
  if (
    named >= 0 &&
    lines[named + 1] &&
    !/view in search|copy list|share list/i.test(lines[named + 1])
  ) {
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

  function decodeBlob(raw) {
    return String(raw || "")
      .replace(/\\u002f/gi, "/")
      .replace(/\\u002d/gi, "-")
      .replace(/\\\//g, "/");
  }

  function toPublic(raw) {
    const blob = decodeBlob(raw);
    const match = blob.match(/(?:https?:\/\/(?:www\.)?)?linkedin\.com\/in\/([^/?#"'\s]+)/i);
    if (!match) return "";
    const slug = match[1].replace(/\/$/, "");
    if (!slug || /^sales/i.test(slug) || slug.startsWith("ACwAA")) return "";
    return "https://www.linkedin.com/in/" + slug;
  }

  function snId(raw) {
    const match = String(raw || "").match(/\/sales\/(?:lead|people)\/([^,/?#]+)/i);
    return match ? match[1] : "";
  }

  function memberId(raw) {
    const match = String(raw || "").match(/ACwAA[A-Za-z0-9_-]{6,}/);
    return match ? match[0] : "";
  }

  function identUrl(raw) {
    const slug = decodeBlob(raw).trim();
    if (!slug || /[/:]/.test(slug) || /^ACwAA/i.test(slug) || /^sales/i.test(slug)) return "";
    return "https://www.linkedin.com/in/" + slug;
  }

  function walkProfiles(value, ids, names) {
    if (!value || typeof value !== "object") return;
    if (Array.isArray(value)) {
      value.forEach((item) => walkProfiles(item, ids, names));
      return;
    }
    const id = memberId(
      value.entityUrn || value.objectUrn || value.profileId || value.memberId || value.objectId || ""
    );
    const pub =
      toPublic(value.flagshipProfileUrl || value.publicProfileUrl || value.profileUrl || "") ||
      identUrl(value.publicIdentifier || "") ||
      identUrl(value.vanityName || "");
    const name = [value.firstName, value.lastName].filter(Boolean).join(" ") || value.fullName || "";
    if (id && pub) ids[id] = pub;
    if (name && pub) names[String(name).toLowerCase()] = pub;
    Object.keys(value).forEach((key) => walkProfiles(value[key], ids, names));
  }

  function ingestText(raw, ids, names) {
    if (!raw || raw.length < 20) return;
    if (!/publicIdentifier|flagshipProfileUrl|fs_salesProfile|vanityName|linkedin\.com\/in\//.test(raw)) {
      return;
    }
    const blob = decodeBlob(raw);
    try {
      walkProfiles(JSON.parse(blob), ids, names);
    } catch (err) {
      /* not a single JSON document */
    }
    let match;
    const pubRe = /publicIdentifier"\s*:\s*"([^"]+)"/gi;
    while ((match = pubRe.exec(blob))) {
      const pub = identUrl(match[1]);
      if (!pub) continue;
      const nearby = blob.slice(Math.max(0, match.index - 800), match.index + 400);
      const id = memberId(nearby);
      if (id) ids[id] = pub;
    }
    const flagRe = /flagshipProfileUrl"\s*:\s*"([^"]+)"/gi;
    while ((match = flagRe.exec(blob))) {
      const pub = toPublic(match[1]);
      if (!pub) continue;
      const nearby = blob.slice(Math.max(0, match.index - 800), match.index + 400);
      const id = memberId(nearby);
      if (id) ids[id] = pub;
    }
  }

  function publicMaps() {
    const ids = {};
    const names = {};
    const captured = document.getElementById("sn-save-captured");
    if (captured && captured.textContent) {
      try {
        const data = JSON.parse(captured.textContent);
        Object.assign(ids, data.ids || {});
        Object.assign(names, data.names || {});
      } catch (err) {
        /* ignore bad capture */
      }
    }
    ingestText(document.documentElement.innerHTML || "", ids, names);
    document.querySelectorAll("code, script").forEach((el) => {
      if (el.id === "sn-save-captured") return;
      ingestText(el.textContent || "", ids, names);
    });
    return { ids, names };
  }

  function lookupPublic(maps, leadHref, name) {
    const id = snId(leadHref) || memberId(leadHref);
    if (id && maps.ids[id]) return maps.ids[id];
    if (id) {
      const prefix = id.slice(0, 18);
      for (const [key, value] of Object.entries(maps.ids)) {
        if (key.slice(0, 18) === prefix) return value;
      }
    }
    const key = String(name || "")
      .replace(/\s+/g, " ")
      .trim()
      .toLowerCase();
    if (key && maps.names[key]) return maps.names[key];
    return "";
  }

  const maps = publicMaps();

  function push(name, titleText, company, location, hrefLead, extra, publicHint) {
    name = (name || "").replace(/\s+/g, " ").trim();
    if (!name || name.length < 2) return;
    hrefLead = (hrefLead || "").split("?")[0];
    if (hrefLead.startsWith("/")) hrefLead = "https://www.linkedin.com" + hrefLead;
    const sn = /\/sales\/(?:lead|people)\//i.test(hrefLead) ? hrefLead : "";
    const id = snId(hrefLead);
    const pub =
      toPublic(publicHint) ||
      toPublic(hrefLead) ||
      lookupPublic(maps, hrefLead, name) ||
      (id ? "https://www.linkedin.com/in/" + id : "");
    const key = (sn || pub || name).toLowerCase();
    if (seen.has(key)) return;
    seen.add(key);
    leads.push({
      name,
      title: (titleText || "").replace(/\s+/g, " ").trim(),
      company: (company || "").replace(/\s+/g, " ").trim(),
      location: (location || "").replace(/\s+/g, " ").trim(),
      linkedin_url: pub,
      sn_url: sn,
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
    const inA = tr.querySelector('a[href*="/in/"]');
    push(
      nameA.innerText,
      tr.querySelector('[data-anonymize="job-title"]')?.innerText || "",
      tr.querySelector('[data-anonymize="company-name"]')?.innerText || "",
      tr.querySelector('[data-anonymize="location"]')?.innerText || "",
      nameA.getAttribute("href") || "",
      dateAdded,
      inA ? inA.getAttribute("href") || inA.href : ""
    );
  }

  if (!leads.length) {
    for (const a of document.querySelectorAll('a[href*="/sales/lead/"], a[href*="/sales/people/"]')) {
      const card = a.closest("li, article, tr, div") || a.parentElement;
      const blob = (card?.innerText || "")
        .split("\n")
        .map((line) => line.replace(/\s+/g, " ").trim())
        .filter(Boolean);
      const inA = card && card.querySelector('a[href*="/in/"]');
      push(
        a.innerText || blob[0],
        blob[1] || "",
        blob[2] || "",
        blob[3] || "",
        a.getAttribute("href") || "",
        "",
        inA ? inA.getAttribute("href") || inA.href : ""
      );
    }
  }

  return {
    href,
    title,
    listName,
    blocked,
    page,
    total,
    count: leads.length,
    sample: lines.slice(0, 30),
    leads,
  };
}

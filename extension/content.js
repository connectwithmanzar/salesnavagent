const JOB_KEY = "snSaveJob";
const HOST_ID = "sn-save-host";
const MAX_PAGES = 40;
const MAX_ATTEMPTS = 4;

function listIdFromUrl(url) {
  const match = String(url || "").match(/\/sales\/lists\/people\/(\d+)/);
  return match ? match[1] : null;
}

function pageUrlFor(url, n) {
  const parsed = new URL(String(url || location.href).split("#")[0]);
  parsed.searchParams.set("page", String(n));
  if (!parsed.searchParams.get("sortCriteria")) {
    parsed.searchParams.set("sortCriteria", "LAST_ACTIVITY");
    parsed.searchParams.set("sortOrder", "DESCENDING");
  }
  return parsed.toString();
}

async function readJob() {
  const stored = await chrome.storage.local.get(JOB_KEY);
  return stored[JOB_KEY] || null;
}

async function writeJob(job) {
  if (!job) {
    await chrome.storage.local.remove(JOB_KEY);
    return;
  }
  await chrome.storage.local.set({ [JOB_KEY]: job });
}

function panelHtml(state) {
  const running = state.status === "running";
  const done = state.status === "done";
  const error = state.status === "error";
  const title = running
    ? "Downloading list"
    : done
      ? "Saved"
      : error
        ? "Could not download"
        : "Sales Nav List Save";
  const body = running
    ? `Page ${state.page || 1} · ${state.leads?.length || 0} leads${
        state.total ? ` of ${state.total}` : ""
      }. Paging slowly in your Chrome session.`
    : done
      ? `${state.leads?.length || 0} leads saved to Downloads`
      : error
        ? state.message || "Try again on this people list."
        : "Download this people list to Excel. It pages through the list slowly, like a person.";
  const action = running
    ? `<button class="ghost" id="sn-cancel" type="button">Cancel</button>`
    : `<button class="primary" id="sn-go" type="button">Download Excel</button>`;
  return `
    <style>
      :host { all: initial; }
      .wrap {
        font-family: Inter, system-ui, -apple-system, Segoe UI, sans-serif;
        width: 280px;
        background: #0f2744;
        color: #fff;
        border-radius: 16px;
        box-shadow: 0 18px 40px rgba(11, 31, 58, 0.35);
        padding: 16px 16px 14px;
        box-sizing: border-box;
      }
      h1 { margin: 0; font-size: 14px; font-weight: 700; letter-spacing: 0.01em; }
      p { margin: 8px 0 14px; font-size: 13px; line-height: 1.4; color: #d7e3f2; }
      button {
        border: 0; cursor: pointer; border-radius: 10px; font-weight: 650;
        font-size: 13px; padding: 10px 12px; width: 100%;
      }
      .primary { background: #3ec6ff; color: #062033; }
      .primary:hover { filter: brightness(1.05); }
      .ghost { background: transparent; color: #c5d4e6; border: 1px solid #3a5573; }
      .bar { height: 4px; background: #1c3b5c; border-radius: 99px; overflow: hidden; margin-bottom: 12px; }
      .bar > span { display: block; height: 100%; background: #3ec6ff; width: var(--pct, 12%); }
    </style>
    <div class="wrap">
      <h1>${title}</h1>
      <p>${body}</p>
      ${running ? `<div class="bar"><span style="--pct:${progressPct(state)}%"></span></div>` : ""}
      ${action}
    </div>
  `;
}

function progressPct(state) {
  const have = state.leads?.length || 0;
  const total = state.total || 0;
  if (total) return Math.max(8, Math.min(100, Math.round((have / total) * 100)));
  return Math.min(90, 10 + (state.page || 1) * 8);
}

function ensureHost() {
  let host = document.getElementById(HOST_ID);
  if (host) return host;
  host = document.createElement("div");
  host.id = HOST_ID;
  host.style.cssText =
    "position:fixed;bottom:24px;right:24px;z-index:2147483647;width:280px;";
  host.attachShadow({ mode: "open" });
  document.documentElement.appendChild(host);
  return host;
}

function render(state) {
  const host = ensureHost();
  host.shadowRoot.innerHTML = panelHtml(state);
  const go = host.shadowRoot.getElementById("sn-go");
  const cancel = host.shadowRoot.getElementById("sn-cancel");
  if (go) go.addEventListener("click", () => startJob());
  if (cancel) cancel.addEventListener("click", () => stopJob());
}

function currentPage() {
  const match = location.href.match(/[?&]page=(\d+)/i);
  return match ? parseInt(match[1], 10) : 1;
}

async function scrapeOnce() {
  let last = {};
  for (let attempt = 0; attempt < MAX_ATTEMPTS; attempt += 1) {
    if (attempt === 0) await humanPause(5000, 8000);
    else await humanPause(2000, 3500);
    if (pageLooksRestricted()) return { blocked: true, leads: [] };
    const data = extractListPage();
    if (data) last = data;
    if (data?.blocked) return data;
    if (data?.leads?.length) return data;
    if (data?.listName && attempt >= 2) return data;
  }
  return last;
}

async function restBetweenPages(job) {
  const n = (job.scrapedPages || []).length;
  if (n > 0 && n % 4 === 0) await humanPause(12000, 22000);
  else await humanPause(6000, 11000);
}

async function moveToNextPage(job) {
  const moved = await goToNextListPage();
  if (moved === "restricted") return "restricted";
  if (moved === "clicked") return "clicked";
  job.page = currentPage() + 1;
  await writeJob(job);
  location.assign(pageUrlFor(job.startUrl || location.href, job.page));
  return "reload";
}

async function startJob() {
  const lid = listIdFromUrl(location.href);
  if (!lid) return;
  const job = {
    status: "running",
    listId: lid,
    startUrl: location.href,
    page: 1,
    leads: [],
    seen: [],
    listName: "",
    total: 0,
    empty: 0,
    message: "",
    fingerprints: [],
  };
  await writeJob(job);
  render(job);
  if (currentPage() !== 1) {
    location.assign(pageUrlFor(location.href, 1));
    return;
  }
  await continueJob(job);
}

async function stopJob() {
  await writeJob(null);
  render({ status: "idle" });
}

async function finishJob(job) {
  if (job.blocked || pageLooksRestricted()) {
    job.status = "error";
    job.message =
      "LinkedIn asked for a check. Stopped. Sign in normally, wait, then try a smaller list later.";
    await writeJob(job);
    render(job);
    return;
  }
  if (!job.leads.length) {
    job.status = "error";
    job.message = "No leads found on this list. Stay on the people-list tab and retry.";
    await writeJob(job);
    render(job);
    return;
  }
  downloadLeads(job.leads, job.listName);
  job.status = "done";
  await writeJob(job);
  render(job);
  setTimeout(() => writeJob(null), 8000);
}

function mergeLeads(job, leads) {
  const seen = new Set(job.seen || []);
  for (const lead of leads) {
    const key = (lead.linkedin_url || lead.name || "").toLowerCase();
    if (!key || seen.has(key)) continue;
    seen.add(key);
    job.leads.push(lead);
  }
  job.seen = Array.from(seen);
}

async function continueJob(job) {
  while (job.status === "running") {
    if (pageLooksRestricted()) {
      job.blocked = true;
      await finishJob(job);
      return;
    }
    render(job);
    await browseListLikeAPerson();
    const data = await scrapeOnce();
    if (data?.blocked || pageLooksRestricted()) {
      job.blocked = true;
      await finishJob(job);
      return;
    }
    if (data?.listName) job.listName = data.listName;
    if (data?.total) job.total = Number(data.total) || job.total;
    const leads = data?.leads || [];
    const fingerprint = listFingerprint();
    job.fingerprints = job.fingerprints || [];
    if (job.fingerprints.includes(fingerprint) && job.leads.length) {
      await finishJob(job);
      return;
    }
    job.fingerprints.push(fingerprint);
    mergeLeads(job, leads);
    job.lastScrapedPage = currentPage();
    job.scrapedPages = job.scrapedPages || [];
    if (!job.scrapedPages.includes(currentPage())) job.scrapedPages.push(currentPage());
    if (!leads.length) job.empty += 1;
    else job.empty = 0;
    job.page = currentPage();
    await writeJob(job);
    render(job);

    const reachedTotal = job.total && job.leads.length >= job.total;
    if (reachedTotal || job.scrapedPages.length >= MAX_PAGES || job.empty >= 2) {
      await finishJob(job);
      return;
    }

    await restBetweenPages(job);
    const latest = await readJob();
    if (!latest || latest.status !== "running") return;
    Object.assign(job, latest);

    const moved = await moveToNextPage(job);
    if (moved === "restricted") {
      job.blocked = true;
      await finishJob(job);
      return;
    }
    if (moved === "reload") return;
  }
}

async function boot() {
  const lid = listIdFromUrl(location.href);
  if (!lid) return;
  const job = await readJob();
  if (job?.status === "running" && job.listId === lid) {
    render(job);
    await continueJob(job);
    return;
  }
  render(job && job.listId === lid ? job : { status: "idle" });
}

chrome.runtime.onMessage.addListener((message, _sender, sendResponse) => {
  if (message?.type === "SN_SAVE_START") {
    startJob().then(() => sendResponse({ ok: true }));
    return true;
  }
  if (message?.type === "SN_SAVE_STATUS") {
    readJob().then((job) => sendResponse({ job, url: location.href }));
    return true;
  }
  return false;
});

boot();

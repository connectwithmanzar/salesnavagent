const LIST_RE = /linkedin\.com\/sales\/lists\/people\/\d+/i;

async function activeTab() {
  const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
  return tab;
}

async function boot() {
  const status = document.getElementById("status");
  const go = document.getElementById("go");
  const tab = await activeTab();
  const url = tab?.url || "";
  if (!LIST_RE.test(url)) {
    status.textContent =
      "Open a Sales Navigator people list, then click the extension. Search results will not work.";
    return;
  }
  go.hidden = false;
  status.textContent = "Download this people list to Excel in your Downloads folder.";
  go.addEventListener("click", async () => {
    go.disabled = true;
    go.textContent = "Starting…";
    try {
      await chrome.tabs.sendMessage(tab.id, { type: "SN_SAVE_START" });
      window.close();
    } catch {
      status.textContent = "Reload the list tab, then click Download Excel again.";
      go.disabled = false;
      go.textContent = "Download Excel";
    }
  });
}

boot();

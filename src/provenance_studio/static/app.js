const state = { runs: [], selected: null, zoom: 1 };
const $ = (selector) => document.querySelector(selector);
const elements = {
  form: $("#generate-form"), prompt: $("#prompt"), token: $("#access-token"),
  generate: $("#generate-button"), lineage: $("#lineage-list"), image: $("#asset-image"),
  empty: $("#empty-asset"), refine: $("#refine-button"), verify: $("#verify-button"),
  download: $("#download-asset"), receipt: $("#receipt-state"), verified: $("#verified-label"),
  status: $("#live-status"), zoomValue: $("#zoom-value"),
};

async function request(path, options = {}) {
  const token = elements.token.value.trim();
  const headers = { ...(options.headers || {}) };
  if (token) headers["X-Demo-Token"] = token;
  const response = await fetch(path, { ...options, headers });
  if (!response.ok) {
    let detail = "Request failed";
    try { detail = (await response.json()).detail || detail; } catch {}
    throw new Error(detail);
  }
  return response.json();
}

function shortId(value) { return value ? `${value.slice(0, 8)}…${value.slice(-4)}` : "—"; }
function setBusy(busy) {
  document.body.classList.toggle("is-loading", busy);
  elements.generate.disabled = busy;
  elements.refine.disabled = busy || !state.selected;
  elements.verify.disabled = busy || !state.selected;
}
function announce(message) { elements.status.textContent = message; }

function renderReceipt(run) {
  const receipt = run?.receipt;
  elements.receipt.className = `receipt-state ${receipt ? (receipt.verified ? "verified" : "failed") : "pending"}`;
  elements.verified.textContent = receipt?.verified ? "Verified" : receipt ? "Failed" : "Verified";
  $("#run-id").textContent = run?.run_id || "—";
  $("#parent-id").textContent = run?.parent_run_id || "—";
  $("#provider").textContent = run?.provider || "—";
  $("#model").textContent = run?.model || "—";
  $("#manifest-hash").textContent = receipt?.manifest_hash || "—";
  $("#asset-hash").textContent = receipt?.assets?.[0]?.observed_sha256 || "—";
}

function renderLineage() {
  elements.lineage.replaceChildren();
  state.runs.forEach((run) => {
    const item = document.createElement("li");
    item.className = run.run_id === state.selected?.run_id ? "selected" : "";
    const button = document.createElement("button");
    button.type = "button";
    button.setAttribute("aria-label", `Select run ${run.run_id}`);
    const image = document.createElement("img");
    image.src = run.asset_url;
    image.alt = "";
    const copy = document.createElement("span");
    copy.className = "lineage-copy";
    const title = document.createElement("strong");
    title.textContent = run.prompt;
    const detail = document.createElement("small");
    detail.textContent = run.parent_run_id ? shortId(run.parent_run_id) : shortId(run.run_id);
    copy.append(title, detail);
    button.append(image, copy);
    button.addEventListener("click", () => selectRun(run));
    item.append(button);
    elements.lineage.append(item);
  });
}

function selectRun(run) {
  state.selected = run;
  state.zoom = 1;
  elements.image.src = run.asset_url;
  elements.image.alt = run.prompt;
  elements.image.hidden = false;
  elements.empty.hidden = true;
  elements.image.style.setProperty("--zoom", state.zoom);
  elements.zoomValue.value = "100%";
  elements.download.href = run.asset_url;
  elements.download.hidden = false;
  elements.refine.disabled = false;
  elements.verify.disabled = false;
  renderReceipt(run);
  renderLineage();
  announce(`Selected ${run.run_id}`);
}

async function loadRuns() {
  const listing = await request("/runs");
  const loaded = await Promise.all(listing.run_ids.map((id) => request(`/runs/${id}`)));
  state.runs = orderByLineage(loaded);
  renderLineage();
  if (state.runs.length) selectRun(state.runs[state.runs.length - 1]);
}

function orderByLineage(runs) {
  const pending = new Map(runs.map((run) => [run.run_id, run]));
  const ordered = [];
  while (pending.size) {
    const ready = [...pending.values()].filter(
      (run) => !run.parent_run_id || !pending.has(run.parent_run_id),
    );
    if (!ready.length) return runs;
    ready.sort((left, right) => left.run_id.localeCompare(right.run_id));
    ready.forEach((run) => { ordered.push(run); pending.delete(run.run_id); });
  }
  return ordered;
}

async function generate(parentRunId = null) {
  const prompt = elements.prompt.value.trim();
  if (!prompt) return;
  setBusy(true);
  announce(parentRunId ? "Refining" : "Generating");
  try {
    const run = await request("/runs", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ prompt, parent_run_id: parentRunId }),
    });
    state.runs.push(run);
    selectRun(run);
    announce(run.receipt.verified ? "Verified" : "Verification failed");
  } catch (error) {
    announce(error.message);
    window.alert(error.message);
  } finally { setBusy(false); }
}

elements.form.addEventListener("submit", (event) => { event.preventDefault(); generate(); });
elements.refine.addEventListener("click", () => generate(state.selected?.run_id));
elements.verify.addEventListener("click", async () => {
  if (!state.selected) return;
  setBusy(true);
  try {
    const receipt = await request(`/runs/${state.selected.run_id}/verify`);
    state.selected = { ...state.selected, receipt };
    state.runs = state.runs.map((run) => run.run_id === state.selected.run_id ? state.selected : run);
    renderReceipt(state.selected);
    announce(receipt.verified ? "Verified" : "Verification failed");
  } catch (error) { announce(error.message); window.alert(error.message); }
  finally { setBusy(false); }
});
$("#toggle-token").addEventListener("click", (event) => {
  const showing = elements.token.type === "text";
  elements.token.type = showing ? "password" : "text";
  event.currentTarget.setAttribute("aria-label", showing ? "Show judge access token" : "Hide judge access token");
});
$("#zoom-out").addEventListener("click", () => updateZoom(-.1));
$("#zoom-in").addEventListener("click", () => updateZoom(.1));
function updateZoom(delta) {
  state.zoom = Math.min(1.5, Math.max(.7, Math.round((state.zoom + delta) * 10) / 10));
  elements.image.style.setProperty("--zoom", state.zoom);
  elements.zoomValue.value = `${Math.round(state.zoom * 100)}%`;
}

loadRuns().catch((error) => announce(error.message));

"use strict";

const $ = (sel) => document.querySelector(sel);

const state = {
  originalUrl: null,   // object URL of the uploaded/example image
  gradcamUrl: null,    // base64 data URI from the API
};

// ---------- helpers --------------------------------------------------------
function pct(p) { return (p * 100).toFixed(1) + "%"; }

function badge(risk) {
  const label = risk === "premalignant" ? "pre-malignant" : risk;
  return `<span class="badge ${risk}">${label}</span>`;
}

function setStatus(msg, isError = false) {
  const el = $("#status");
  if (!msg) { el.classList.add("hidden"); return; }
  el.textContent = msg;
  el.classList.toggle("error", isError);
  el.classList.remove("hidden");
}

// ---------- prediction -----------------------------------------------------
async function predict(file) {
  if (state.originalUrl) URL.revokeObjectURL(state.originalUrl);
  state.originalUrl = URL.createObjectURL(file);

  $("#results").classList.add("hidden");
  setStatus("Analyzing…");

  const form = new FormData();
  form.append("file", file);

  let res;
  try {
    res = await fetch("/api/predict", { method: "POST", body: form });
  } catch (e) {
    setStatus("Network error — is the server running?", true);
    return;
  }

  if (res.status === 503) {
    setStatus(
      "The model has not been trained yet. Run the training notebook and place "
      + "model.keras in the webapp/model/ directory, then try again.",
      true
    );
    return;
  }
  if (!res.ok) {
    const detail = await res.json().catch(() => ({}));
    setStatus(detail.detail || "Prediction failed.", true);
    return;
  }

  const data = await res.json();
  setStatus(null);
  renderResults(data);
}

async function predictExampleUrl(url) {
  setStatus("Loading example…");
  try {
    const blob = await (await fetch(url)).blob();
    await predict(new File([blob], "example.jpg", { type: blob.type }));
  } catch (e) {
    setStatus("Could not load example image.", true);
  }
}

function renderResults(data) {
  // image + grad-cam
  state.gradcamUrl = data.gradcam_png || null;
  $("#preview-img").src = state.originalUrl;
  setView("original");

  const hasGradcam = Boolean(state.gradcamUrl);
  $("#view-toggle").hidden = !hasGradcam;
  $("#gradcam-hint").hidden = !hasGradcam;

  // prediction head
  const p = data.predicted;
  $("#prediction-head").innerHTML =
    `<h3 class="pred-name">${p.short_name}</h3>`
    + badge(p.risk)
    + `<span class="pred-prob">${pct(p.probability)} confidence</span>`;
  $("#prediction-desc").textContent = data.description;

  // bars (all classes, already sorted desc)
  $("#bars").innerHTML = data.all_scores.map((s, i) => {
    const cls = [
      "bar-row",
      i === 0 ? "top" : "",
      s.concerning ? "concerning" : "",
    ].join(" ").trim();
    return `
      <div class="${cls}">
        <div class="bar-label">
          <span class="name">${s.short_name}</span>
          <span class="muted">${pct(s.probability)}</span>
        </div>
        <div class="bar-track"><div class="bar-fill" style="width:${pct(s.probability)}"></div></div>
      </div>`;
  }).join("");

  $("#results").classList.remove("hidden");
  $("#results").scrollIntoView({ behavior: "smooth", block: "nearest" });
}

// ---------- original / grad-cam toggle ------------------------------------
function setView(view) {
  const img = $("#preview-img");
  img.src = view === "gradcam" && state.gradcamUrl ? state.gradcamUrl : state.originalUrl;
  document.querySelectorAll("#view-toggle button").forEach((b) =>
    b.classList.toggle("active", b.dataset.view === view)
  );
}

// ---------- examples & about ----------------------------------------------
async function loadExamples() {
  try {
    const items = await (await fetch("/api/examples")).json();
    const gallery = $("#example-gallery");
    if (!items.length) {
      gallery.innerHTML = '<span class="muted small">No example images available yet.</span>';
      return;
    }
    gallery.innerHTML = items.map((it) =>
      `<div class="example-thumb" data-url="${it.url}" title="${it.name}">
         <img src="${it.url}" alt="${it.name}" loading="lazy" />
         <span>${it.code}</span>
       </div>`
    ).join("");
    gallery.querySelectorAll(".example-thumb").forEach((el) =>
      el.addEventListener("click", () => predictExampleUrl(el.dataset.url))
    );
  } catch (e) { /* leave gallery empty */ }
}

async function loadAbout() {
  let data;
  try {
    data = await (await fetch("/api/about")).json();
  } catch (e) { return; }

  if (data.disclaimer) {
    $("#disclaimer-text").textContent = data.disclaimer;
    $("#footer-disclaimer").textContent = data.disclaimer;
  }

  const el = $("#about-content");
  if (!data.model_available || !data.report) {
    el.innerHTML = '<p class="muted">Model metrics will appear here once the model is trained and its artifacts are added to webapp/model/.</p>';
    return;
  }

  const r = data.report;
  const rows = data.labels.map((lbl) => {
    const m = r[lbl] || {};
    return `<tr>
      <td>${lbl}</td>
      <td>${(m.precision ?? 0).toFixed(2)}</td>
      <td>${(m.recall ?? 0).toFixed(2)}</td>
      <td>${(m["f1-score"] ?? 0).toFixed(2)}</td>
      <td>${m.support ?? 0}</td>
    </tr>`;
  }).join("");

  el.innerHTML = `
    <div class="stat-row">
      <div class="stat">
        <div class="value">${(data.accuracy * 100).toFixed(1)}%</div>
        <div class="label">Validation accuracy</div>
      </div>
      <div class="stat">
        <div class="value">${data.labels.length}</div>
        <div class="label">Diagnostic classes</div>
      </div>
    </div>
    <table class="metrics">
      <thead><tr><th>Class</th><th>Precision</th><th>Recall</th><th>F1</th><th>Support</th></tr></thead>
      <tbody>${rows}</tbody>
    </table>
    ${data.confusion_matrix_url
      ? `<img class="cm-img" src="${data.confusion_matrix_url}" alt="Confusion matrix" />`
      : ""}
  `;
}

// ---------- wiring ---------------------------------------------------------
function initDropzone() {
  const dz = $("#dropzone");
  const input = $("#file-input");

  dz.addEventListener("click", () => input.click());
  dz.addEventListener("keydown", (e) => {
    if (e.key === "Enter" || e.key === " ") { e.preventDefault(); input.click(); }
  });
  input.addEventListener("change", () => {
    if (input.files[0]) predict(input.files[0]);
  });

  ["dragenter", "dragover"].forEach((ev) =>
    dz.addEventListener(ev, (e) => { e.preventDefault(); dz.classList.add("dragover"); })
  );
  ["dragleave", "drop"].forEach((ev) =>
    dz.addEventListener(ev, (e) => { e.preventDefault(); dz.classList.remove("dragover"); })
  );
  dz.addEventListener("drop", (e) => {
    const file = e.dataTransfer.files[0];
    if (file) predict(file);
  });
}

function init() {
  initDropzone();
  document.querySelectorAll("#view-toggle button").forEach((b) =>
    b.addEventListener("click", () => setView(b.dataset.view))
  );
  loadExamples();
  loadAbout();
}

document.addEventListener("DOMContentLoaded", init);

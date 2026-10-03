const $ = (id) => document.getElementById(id);
let mode = "role";
let roles = [];

async function api(path, opts) {
  const res = await fetch(path, opts);
  const data = await res.json().catch(() => ({}));
  if (!res.ok) throw new Error(data.error || "Something went wrong");
  return data;
}

const esc = (s) => String(s).replace(/[&<>"']/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));
const scoreColor = (n) => (n >= 75 ? "#12805c" : n >= 45 ? "#ca8a04" : "#c2410c");

// ---------- Roles ----------
async function loadRoles() {
  roles = await api("/api/roles");
  $("role").innerHTML = roles.map((r) => `<option value="${r.id}">${esc(r.title)}</option>`).join("");
  showRoleDesc();
}
function showRoleDesc() {
  const r = roles.find((x) => x.id == $("role").value);
  $("roleDesc").textContent = r ? `${r.description} (${r.skill_count} skills tracked)` : "";
}
$("role").addEventListener("change", showRoleDesc);

// ---------- Tabs ----------
document.querySelectorAll(".tab").forEach((t) =>
  t.addEventListener("click", () => {
    mode = t.dataset.mode;
    document.querySelectorAll(".tab").forEach((x) => x.classList.toggle("active", x === t));
    $("rolePane").hidden = mode !== "role";
    $("jdPane").hidden = mode !== "jd";
  })
);

// ---------- File upload ----------
async function uploadFile(file) {
  $("error").textContent = "";
  const fd = new FormData();
  fd.append("file", file);
  $("drop").innerHTML = "Reading " + esc(file.name) + "…";
  try {
    const { text } = await api("/api/extract-text", { method: "POST", body: fd });
    $("resume").value = text;
    $("drop").classList.add("done");
    $("drop").innerHTML = "✓ " + esc(file.name) + " loaded – click to replace";
  } catch (e) {
    $("drop").classList.remove("done");
    $("drop").innerHTML = "<strong>Click to upload</strong> or drop a PDF, DOCX, TXT";
    $("error").textContent = e.message;
  }
}
$("file").addEventListener("change", (e) => e.target.files[0] && uploadFile(e.target.files[0]));
["dragover", "dragenter"].forEach((ev) => $("drop").addEventListener(ev, (e) => { e.preventDefault(); $("drop").classList.add("over"); }));
["dragleave", "drop"].forEach((ev) => $("drop").addEventListener(ev, (e) => { e.preventDefault(); $("drop").classList.remove("over"); }));
$("drop").addEventListener("drop", (e) => e.dataTransfer.files[0] && uploadFile(e.dataTransfer.files[0]));

// ---------- Analyze ----------
$("analyzeBtn").addEventListener("click", async () => {
  $("error").textContent = "";
  const body = { resume_text: $("resume").value };
  if (mode === "role") body.role_id = Number($("role").value);
  else body.job_description = $("jd").value;

  $("analyzeBtn").disabled = true;
  $("analyzeBtn").textContent = "Analyzing…";
  try {
    const data = await api("/api/analyze", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(body),
    });
    render(data);
    loadHistory();
  } catch (e) {
    $("error").textContent = e.message;
  } finally {
    $("analyzeBtn").disabled = false;
    $("analyzeBtn").textContent = "Analyze my resume";
  }
});

function render(d) {
  $("results").hidden = false;
  $("resTitle").textContent = "Match for: " + d.target;
  $("scoreNum").textContent = d.score;
  $("ring").style.setProperty("--p", d.score);
  $("ring").style.setProperty("--ringc", scoreColor(d.score));
  const req = d.missing.filter((s) => s.importance === "required").length;
  $("resSummary").textContent = d.missing.length
    ? `You're missing ${d.missing.length} skill${d.missing.length > 1 ? "s" : ""}` + (req ? `, ${req} of them required. Start with those.` : ", all optional extras.")
    : "Great news – your resume covers every skill we track for this role.";
  $("missCount").textContent = d.missing.length;
  $("haveCount").textContent = d.matched.length;

  $("missing").innerHTML = d.missing.length
    ? d.missing.map((s) => `
      <div class="gap ${s.importance}">
        <div class="top"><b>${esc(s.name)}</b><span class="tag">${s.importance}</span></div>
        <small>${esc(s.category)}</small>
        ${s.resource ? `<div><a href="${esc(s.resource)}" target="_blank" rel="noopener">Learn it →</a></div>` : ""}
      </div>`).join("")
    : '<p class="muted">Nothing missing 🎉</p>';

  $("matched").innerHTML = d.matched.length
    ? d.matched.map((s) => `<span class="chip">${esc(s.name)}</span>`).join("")
    : '<span class="muted">None of the target skills were found.</span>';
  $("extra").innerHTML = d.extra_skills.length
    ? d.extra_skills.map((s) => `<span class="chip plain">${esc(s)}</span>`).join("")
    : '<span class="muted">—</span>';

  $("results").scrollIntoView({ behavior: "smooth", block: "start" });
}

// ---------- History ----------
async function loadHistory() {
  const list = await api("/api/history");
  $("history").innerHTML = list.length
    ? list.map((h) => `
      <div class="hist">
        <div class="score" style="color:${scoreColor(h.score)}">${h.score}%</div>
        <div class="info"><div>${esc(h.target)}</div>
          <div class="muted">${esc(h.created_at)} UTC · missing: ${esc(h.missing.slice(0, 4).join(", ") || "none")}${h.missing.length > 4 ? "…" : ""}</div></div>
        <button title="Delete" data-id="${h.id}">✕</button>
      </div>`).join("")
    : "No analyses yet.";
}
$("history").addEventListener("click", async (e) => {
  const id = e.target.dataset.id;
  if (!id) return;
  await api("/api/history/" + id, { method: "DELETE" });
  loadHistory();
});
$("refreshHistory").addEventListener("click", loadHistory);

loadRoles();
loadHistory();

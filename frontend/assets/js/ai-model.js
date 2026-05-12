// ══════════════════════════════════════════
// 🤖 AI Model — Frontend Integration
// ══════════════════════════════════════════

// ── Tab Switcher ──────────────────────────
function showTab(name) {
  // Hide all panels
  document.querySelectorAll(".ai-panel").forEach(p => p.style.display = "none");
  document.querySelectorAll(".ai-tab").forEach(t => t.classList.remove("active"));

  // Show selected
  document.getElementById("tab-" + name).style.display = "block";
  event.target.closest(".ai-tab").classList.add("active");
}

// ── Helper : build HTML table ─────────────
function buildTable(data) {
  if (!data || data.length === 0) return "<p style='color:#888;'>Aucun résultat.</p>";

  const headers = Object.keys(data[0]);
  let html = `<table class="ai-table"><thead><tr>`;
  headers.forEach(h => html += `<th>${h}</th>`);
  html += `</tr></thead><tbody>`;

  data.forEach(row => {
    html += `<tr>`;
    headers.forEach(h => {
      let val = row[h];

      // Badge for classification
      if (h === "classification") {
        const cls = val === "Excellent" ? "excellent" : val === "Moyen" ? "moyen" : "faible";
        val = `<span class="badge badge-${cls}">${val}</span>`;
      }

      // Badge for bias_type
      if (h === "bias_type" && val) {
        const cls = val === "Trop sévère" ? "severe" : "generous";
        val = `<span class="badge badge-${cls}">${val}</span>`;
      }

      // Boolean
      if (typeof val === "boolean") {
        val = val
          ? `<span style="color:#dc3545; font-weight:700;">⚠️ Oui</span>`
          : `<span style="color:#28a745; font-weight:700;">✅ Non</span>`;
      }

      // Round numbers
      if (typeof val === "number") val = Math.round(val * 100) / 100;

      html += `<td>${val ?? "—"}</td>`;
    });
    html += `</tr>`;
  });

  html += `</tbody></table>`;
  return html;
}

// ══════════════════════════════════════════
// 1. CLASSIFICATION
// ══════════════════════════════════════════
async function loadClassification() {
  const loading = document.getElementById("classify-loading");
  const result  = document.getElementById("classify-result");
  const metrics = document.getElementById("classify-metrics");

  loading.style.display = "block";
  result.innerHTML = "";
  metrics.style.display = "none";

  try {
    const data = await getData("/stats/classify-works");

    loading.style.display = "none";

    if (!data || data.length === 0) {
      result.innerHTML = "<p style='color:#888;'>Aucun travail trouvé.</p>";
      return;
    }

    // Count by classification
    const counts = { Excellent: 0, Moyen: 0, Faible: 0 };
    data.forEach(d => { if (counts[d.classification] !== undefined) counts[d.classification]++; });

    document.getElementById("count-excellent").innerText = counts.Excellent;
    document.getElementById("count-moyen").innerText     = counts.Moyen;
    document.getElementById("count-faible").innerText    = counts.Faible;
    metrics.style.display = "flex";

    result.innerHTML = buildTable(data);

  } catch (e) {
    loading.style.display = "none";
    result.innerHTML = `<p style="color:red;">❌ Erreur : ${e.message}</p>`;
  }
}

// ══════════════════════════════════════════
// 2. SIMILARITÉ
// ══════════════════════════════════════════
async function loadSimilar() {
  const workId  = document.getElementById("work-id-input").value;
  const loading = document.getElementById("similar-loading");
  const result  = document.getElementById("similar-result");

  if (!workId) {
    result.innerHTML = "<p style='color:orange;'>⚠️ Veuillez entrer un work_id.</p>";
    return;
  }

  loading.style.display = "block";
  result.innerHTML = "";

  try {
    const data = await getData(`/stats/similar-works/${workId}`);
    loading.style.display = "none";

    if (data.message) {
      result.innerHTML = `<p style="color:#888;">${data.message}</p>`;
      return;
    }

    if (!data.similar_works || data.similar_works.length === 0) {
      result.innerHTML = "<p style='color:#888;'>Aucun travail similaire trouvé.</p>";
      return;
    }

    result.innerHTML = `
      <p style="margin-bottom:0.5rem; color:#555;">
        Travaux similaires au work <strong>#${workId}</strong> :
      </p>
      ${buildTable(data.similar_works)}
    `;

  } catch (e) {
    loading.style.display = "none";
    result.innerHTML = `<p style="color:red;">❌ Erreur : ${e.message}</p>`;
  }
}

// ══════════════════════════════════════════
// 3. REVIEWERS BIAISÉS
// ══════════════════════════════════════════
async function loadBiased() {
  const threshold = document.getElementById("threshold-input").value || 3;
  const loading   = document.getElementById("biased-loading");
  const result    = document.getElementById("biased-result");

  loading.style.display = "block";
  result.innerHTML = "";

  try {
    const data = await getData(`/stats/biased-reviewers?threshold=${threshold}`);
    loading.style.display = "none";

    if (!data || data.length === 0) {
      result.innerHTML = `
        <p style="color:#28a745; font-weight:600;">
          ✅ Aucun reviewer biaisé détecté avec un seuil de ${threshold}.
        </p>`;
      return;
    }

    result.innerHTML = `
      <p style="color:#dc3545; font-weight:600; margin-bottom:0.5rem;">
        ⚠️ ${data.length} reviewer(s) biaisé(s) détecté(s) :
      </p>
      ${buildTable(data)}
    `;

  } catch (e) {
    loading.style.display = "none";
    result.innerHTML = `<p style="color:red;">❌ Erreur : ${e.message}</p>`;
  }
}

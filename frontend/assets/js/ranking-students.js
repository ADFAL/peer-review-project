let data = [];
let filtered = [];
let page = 1;
const perPage = 10;

async function load() {
  try {
    data = await getData("/ranking/students");
    filtered = data || [];

    render();
    showTop3(); // ⭐ NEW
  } catch (error) {
    console.error("Error loading ranking:", error);
  }
}

function render() {
  const table = document.getElementById("table");
  if (!table) return;

  table.innerHTML = "";

  const start = (page - 1) * perPage;
  const end = start + perPage;

  const pageData = filtered.slice(start, end);

  pageData.forEach((d) => {
    table.innerHTML += `
      <tr>
        <td>${d?.student_id || "N/A"}</td>
        <td>${d?.score ?? d?.note ?? 0}</td>
      </tr>
    `;
  });

  const loading = document.getElementById("loading");
  if (loading) loading.style.display = "none";
}

function getScore(s) {
  return Number(s.score ?? s.note ?? s.rating ?? 0);
}

function showTop3() {
  const top3 = [...filtered]
    .sort((a, b) => getScore(b) - getScore(a))
    .slice(0, 3);

  const container = document.getElementById("top3");
  if (!container) return;

  container.innerHTML = "";

  top3.forEach((s, index) => {
    container.innerHTML += `
      <div class="card">
        <h3>
          ${index === 0 ? "🥇" : index === 1 ? "🥈" : "🥉"}
          Student ${s.student_id || s.id}
        </h3>
        <p>Score: ${getScore(s)}</p>
      </div>
    `;
  });
}

function nextPage() {
  if (page < filtered.length / perPage) {
    page++;
    render();
  }
}

function prevPage() {
  if (page > 1) {
    page--;
    render();
  }
}

load();
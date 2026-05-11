let reviews = [];
let filtered = [];
let page = 1;
const perPage = 10;

async function loadReviews() {
  try {
    reviews = await getData("/reviews");
    filtered = reviews || [];

    setupSearch();
    render();
  } catch (error) {
    console.error("Error loading reviews:", error);
  }
}

function getNote(r) {
  return r?.note || r?.score || r?.rating || "No Note";
}

function render() {
  const table = document.getElementById("table");
  if (!table) return;

  table.innerHTML = "";

  const start = (page - 1) * perPage;
  const end = start + perPage;

  const pageData = filtered.slice(start, end);

  pageData.forEach((r) => {
    table.innerHTML += `
      <tr>
        <td>${r?.id || "N/A"}</td>
        <td>${r?.work_id || r?.work || "N/A"}</td>
        <td>${getNote(r)}</td>
      </tr>
    `;
  });

  const loading = document.getElementById("loading");
  if (loading) loading.style.display = "none";

  const pageInfo = document.getElementById("pageInfo");
  if (pageInfo) {
    pageInfo.innerText = `Page ${page} / ${Math.ceil(filtered.length / perPage)}`;
  }
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

function setupSearch() {
  const input = document.getElementById("search");

  if (!input) return; // FIX: prevents crash if input missing

  input.addEventListener("input", function (e) {
    const value = (e.target.value || "").toLowerCase();

    filtered = reviews.filter((r) => {
      const work = String(r?.work || r?.work_id || "").toLowerCase();
      const note = String(getNote(r)).toLowerCase();
      const id = String(r?.id || "").toLowerCase();

      return (
        work.includes(value) ||
        note.includes(value) ||
        id.includes(value)
      );
    });

    page = 1;
    render();
  });
}

loadReviews();
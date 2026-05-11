let works = [];
let filtered = [];
let page = 1;
const perPage = 10;

async function loadWorks() {
  works = await getData("/works");
  filtered = works;

  setupSearch();
  render();
}

function render() {
  const table = document.getElementById("table");
  table.innerHTML = "";

  const start = (page - 1) * perPage;
  const end = start + perPage;

  const pageData = filtered.slice(start, end);

  pageData.forEach((w) => {
    table.innerHTML += `
      <tr>
        <td>${w.id}</td>
        <td>${w.title || "No Title"}</td>
        <td>${w.description || "No Description"}</td>
      </tr>
    `;
  });

  document.getElementById("loading").style.display = "none";

  document.getElementById("pageInfo").innerText =
    `Page ${page} / ${Math.ceil(filtered.length / perPage)}`;
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

  input.addEventListener("input", function (e) {
    const value = e.target.value.toLowerCase();

    filtered = works.filter((w) =>
      (w.title || "").toLowerCase().includes(value) ||
      (w.description || "").toLowerCase().includes(value)
    );

    page = 1; // reset page
    render();
  });
}

loadWorks();
let students = [];
let filtered = [];
let page = 1;
const perPage = 10;

async function loadStudents(){
  students = await getData("/students");
  filtered = students;

  setupSearch();
  render();
}

function getName(s){
  return s.name || s.full_name || `${s.first_name || ""} ${s.last_name || ""}`.trim() || "No Name";
}

function render(){

  const table = document.getElementById("table");
  table.innerHTML = "";

  const start = (page - 1) * perPage;
  const end = start + perPage;

  const pageData = filtered.slice(start, end);

  pageData.forEach(s=>{
    table.innerHTML += `
      <tr>
        <td>${s.id}</td>
        <td>${getName(s)}</td>
        <td>${s.email || "N/A"}</td>
      </tr>
    `;
  });

  document.getElementById("loading").style.display = "none";
}

function nextPage(){
  if(page < filtered.length / perPage){
    page++;
    render();
  }
}

function prevPage(){
  if(page > 1){
    page--;
    render();
  }
}

function setupSearch(){
  const input = document.getElementById("search");

  input.addEventListener("input", function(e){
    const value = e.target.value.toLowerCase();

    filtered = students.filter(s =>
      getName(s).toLowerCase().includes(value) ||
      (s.email || "").toLowerCase().includes(value)
    );

    page = 1; // reset page
    render();
  });
}

loadStudents();
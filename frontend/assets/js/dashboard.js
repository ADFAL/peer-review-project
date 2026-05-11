async function loadStats(){
  const data = await getData("/stats");

  document.getElementById("students").innerText = data.students;
  document.getElementById("works").innerText = data.works;
  document.getElementById("reviews").innerText = data.reviews;

  const ctx = document.getElementById("chart");

  new Chart(ctx, {
    type: "bar",
    data: {
      labels: ["Students", "Works", "Reviews"],
      datasets: [{
        data: [data.students, data.works, data.reviews]
      }]
    }
  });
}

loadStats();
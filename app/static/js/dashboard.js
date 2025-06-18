document.addEventListener('DOMContentLoaded', async () => {
  // Fetch the JSON data
  const resp = await fetch('/api/dashboard-data');
  if (!resp.ok) {
    console.error('Failed to load dashboard data', resp.status);
    return;
  }
  const data = await resp.json();

  // 1) By Status (Pie)
  new Chart(
    document.getElementById('statusChart'),
    {
      type: 'pie',
      data: {
        labels: data.statuses,
        datasets: [{ data: data.status_counts }]
      }
    }
  );

  // 2) Top Categories (Bar)
  new Chart(
    document.getElementById('categoryChart'),
    {
      type: 'bar',
      data: {
        labels: data.cat_names,
        datasets: [{
          label: 'Incidents',
          data: data.cat_counts
        }]
      },
      options: {
        scales: { y: { beginAtZero: true } }
      }
    }
  );

  // 3) Incidents Over Time (Line)
  new Chart(
    document.getElementById('timeChart'),
    {
      type: 'line',
      data: {
        labels: data.dates,
        datasets: [{
          label: 'Incidents',
          data: data.daily_counts,
          tension: 0.3
        }]
      },
      options: {
        scales: {
          x: {
            ticks: { maxRotation: 90, minRotation: 45 }
          }
        }
      }
    }
  );

  // 4) Average resolution time
  document.getElementById('avgTime').textContent = data.avg_hours;
});

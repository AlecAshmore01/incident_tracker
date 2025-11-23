document.addEventListener('DOMContentLoaded', async () => {
  // Modern color palette matching the design system
  const colors = {
    primary: '#6366f1',
    primaryDark: '#4f46e5',
    success: '#10b981',
    warning: '#f59e0b',
    danger: '#ef4444',
    info: '#3b82f6',
    closed: '#6b7280',
    gradient1: '#667eea',
    gradient2: '#764ba2'
  };

  // Status color mapping
  const statusColors = {
    'Open': colors.info,
    'In Progress': colors.warning,
    'Resolved': colors.success,
    'Closed': colors.closed
  };

  // Fetch the JSON data
  const resp = await fetch('/api/dashboard-data');
  if (!resp.ok) {
    console.error('Failed to load dashboard data', resp.status);
    return;
  }
  const data = await resp.json();

  // Generate colors for status chart
  const statusChartColors = data.statuses.map(status => statusColors[status] || colors.primary);

  // 1) By Status (Pie)
  new Chart(
    document.getElementById('statusChart'),
    {
      type: 'pie',
      data: {
        labels: data.statuses,
        datasets: [{
          data: data.status_counts,
          backgroundColor: statusChartColors,
          borderWidth: 2,
          borderColor: '#fff'
        }]
      },
      options: {
        plugins: {
          legend: {
            position: 'bottom',
            labels: {
              padding: 15,
              font: {
                size: 12,
                weight: '500'
              }
            }
          }
        }
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
          data: data.cat_counts,
          backgroundColor: `linear-gradient(135deg, ${colors.gradient1} 0%, ${colors.gradient2} 100%)`,
          backgroundColor: colors.primary,
          borderRadius: 8,
          borderSkipped: false
        }]
      },
      options: {
        responsive: true,
        plugins: {
          legend: {
            display: false
          }
        },
        scales: {
          y: {
            beginAtZero: true,
            grid: {
              color: '#e2e8f0'
            },
            ticks: {
              stepSize: 1
            }
          },
          x: {
            grid: {
              display: false
            }
          }
        }
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
          tension: 0.4,
          borderColor: colors.primary,
          backgroundColor: `rgba(99, 102, 241, 0.1)`,
          borderWidth: 3,
          fill: true,
          pointRadius: 4,
          pointHoverRadius: 6,
          pointBackgroundColor: colors.primary,
          pointBorderColor: '#fff',
          pointBorderWidth: 2
        }]
      },
      options: {
        responsive: true,
        plugins: {
          legend: {
            display: false
          }
        },
        scales: {
          y: {
            beginAtZero: true,
            grid: {
              color: '#e2e8f0'
            },
            ticks: {
              stepSize: 1
            }
          },
          x: {
            grid: {
              color: '#e2e8f0'
            },
            ticks: {
              maxRotation: 90,
              minRotation: 45
            }
          }
        }
      }
    }
  );

  // 4) Average resolution time
  const avgTimeElement = document.getElementById('avgTime');
  if (avgTimeElement) {
    avgTimeElement.textContent = data.avg_hours || '0';
  }
});

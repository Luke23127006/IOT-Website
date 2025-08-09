// ----- Chart.js (unchanged) -----
const ctx = document.getElementById('pred-chart');
if (ctx) {
    new Chart(ctx, {
        type: 'line',
        data: {
            labels: ['25-07-01', '25-07-05', '25-07-10', '25-07-15', '25-07-20', '25-07-25'],
            datasets: [{ label: 'Gas Concentration', data: [63.31, 102.9, 185.69, 82.14, 137.77, 85.24], fill: false, borderWidth: 2, tension: .35, pointRadius: 3 }]
        },
        options: { responsive: true, plugins: { legend: { display: false } }, scales: { y: { beginAtZero: true, ticks: { stepSize: 40 } } } }
    });
}
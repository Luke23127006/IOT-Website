const gasValueSpan = document.getElementById("gas-value");
const ctx = document.getElementById("gas-chart").getContext("2d");

const gasChart = new Chart(ctx, {
    type: 'line',
    data: {
        labels: [],
        datasets: [{
            label: 'Gas Concentration (ppm)',
            data: [],
            borderColor: 'red',
            borderWidth: 2,
            tension: 0.35,
            pointRadius: 3,
            fill: false
        }]
    },
    options: {
        responsive: true,
        scales: {
            x: { display: true },
            y: { beginAtZero: true }
        }
    }
});

// Fake data simulation
setInterval(() => {
    const gasValue = Math.floor(Math.random() * 500);
    gasValueSpan.textContent = gasValue;

    const now = new Date().toLocaleTimeString();
    gasChart.data.labels.push(now);
    gasChart.data.datasets[0].data.push(gasValue);

    if (gasChart.data.labels.length > 10) {
        gasChart.data.labels.shift();
        gasChart.data.datasets[0].data.shift();
    }

    gasChart.update();
}, 2000);
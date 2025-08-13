const canvas = document.getElementById('pred-chart');
let predChart = null;

if (canvas) {
    const ctx = canvas.getContext('2d');
    predChart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: [],
            datasets: [{
                label: 'Prediction (ppm)',
                data: [],
                borderColor: 'blue',
                borderWidth: 2,
                tension: 0.35,
                pointRadius: 2,
                fill: false
            }]
        },
        options: {
            responsive: true,
            animation: false,
            scales: {
                x: { display: true, ticks: { autoSkip: false } },
                y: { beginAtZero: true }
            },
            plugins: { legend: { display: true } }
        }
    });

    // Lần đầu load khi mở trang
    (async () => {
        try {
            const res = await fetch('/api/mq2/predict?horizon=10');
            const data = await res.json();
            predChart.data.labels = data.labels || [];
            predChart.data.datasets[0].data = data.mid || [];
            predChart.update();
        } catch (err) {
            console.warn('predict init fetch error', err);
        }
    })();
}

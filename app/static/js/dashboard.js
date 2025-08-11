// dashboard.js
const gasValueSpan = document.getElementById("gas-value");
const ctx = document.getElementById("gas-chart").getContext("2d");

const MAX_POINTS = 10; // tối đa điểm hiển thị
let lastTs = null;

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
            pointRadius: 2,
            fill: false
        }]
    },
    options: {
        responsive: true,
        animation: false,
        scales: {
            x: { display: true, ticks: { autoSkip: true, maxTicksLimit: 6 } },
            y: { beginAtZero: true }
        },
        plugins: {
            legend: { display: true }
        }
    }
});

function seedChart(labels, values) {
    gasChart.data.labels = labels;
    gasChart.data.datasets[0].data = values;
    gasChart.update();
    if (values.length) gasValueSpan.textContent = values[values.length - 1];
}

async function fetchHistory() {
    try {
        const res = await fetch('/api/mq2/history?limit=10');
        const data = await res.json();
        seedChart(data.labels || [], data.ppm || []);
        lastTs = data.lastTs || null;
    } catch (e) {
        console.warn('fetchHistory error', e);
    }
}

function appendPoint(label, value) {
    gasChart.data.labels.push(label);
    gasChart.data.datasets[0].data.push(value);

    // cắt đuôi nếu quá dài
    if (gasChart.data.labels.length > MAX_POINTS) {
        gasChart.data.labels.shift();
        gasChart.data.datasets[0].data.shift();
    }
    gasChart.update();

    gasValueSpan.textContent = value;
}

async function pollLatest() {
    try {
        const res = await fetch('/api/mq2/latest');
        const doc = await res.json();
        if (!doc || !doc.ts) return;

        if (!lastTs || doc.ts > lastTs) {
            const label = `${doc.time || ''} ${doc.date || ''}`.trim() || new Date(doc.ts).toLocaleTimeString();
            appendPoint(label, doc.ppm ?? 0);
            lastTs = doc.ts;
        }
    } catch (e) {
        console.warn('pollLatest error', e);
    }
}

document.addEventListener('DOMContentLoaded', async () => {
    await fetchHistory();

    setInterval(pollLatest, 2000);
});

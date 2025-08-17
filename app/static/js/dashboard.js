const gasValueSpan = document.getElementById("gas-value");
const tempValueSpan = document.getElementById("dht-temp");
const ctx = document.getElementById("gas-chart").getContext("2d");

const MAX_POINTS = 10;
let lastTs = null;

const WARNING_THRESHOLD = 400;
const DANGER_THRESHOLD = 500;

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
        plugins: { legend: { display: true } }
    }
});

const gasLevelSpan = document.getElementById("gas-level");

function updateLevel(value) {
    const v = Number(value) || 0;
    if (v >= DANGER_THRESHOLD) {
        gasLevelSpan.textContent = "Level: DANGER";
        gasLevelSpan.style.color = "red";
    } else if (v >= WARNING_THRESHOLD) {
        gasLevelSpan.textContent = "Level: WARNING";
        gasLevelSpan.style.color = "orange";
    } else {
        gasLevelSpan.textContent = "Level: NORMAL";
        gasLevelSpan.style.color = "green";
    }
}

function seedChart(labels, values) {
    gasChart.data.labels = labels;
    gasChart.data.datasets[0].data = values;
    gasChart.update();
    if (values.length) {
        const latest = Number(values[values.length - 1]) || 0;
        gasValueSpan.textContent = latest;
        updateLevel(latest);
    }
}

async function fetchHistory() {
    try {
        const res = await fetch('/api/mq2/history?limit=10');
        const data = await res.json();
        const ppmArr = Array.isArray(data.ppm) ? data.ppm.map(x => Number(x) || 0) : [];
        seedChart(data.labels || [], ppmArr);
        lastTs = data.lastTs || null;
        if (!ppmArr.length) updateLevel(0);
    } catch (e) {
        console.warn('fetchHistory error', e);
    }
}

// ====== Prediction Chart cập nhật ở đây ======
async function loadPrediction() {
    try {
        const res = await fetch('/api/mq2/predict?horizon=10');
        const data = await res.json();
        if (predChart) {
            predChart.data.labels = data.labels || [];
            predChart.data.datasets[0].data = data.mid || [];
            predChart.update();
        }
    } catch (err) {
        console.warn('predict fetch error', err);
    }
}

function appendPoint(label, value) {
    const v = Number(value) || 0;
    gasChart.data.labels.push(label);
    gasChart.data.datasets[0].data.push(v);

    if (gasChart.data.labels.length > MAX_POINTS) {
        gasChart.data.labels.shift();
        gasChart.data.datasets[0].data.shift();
    }
    gasChart.update();

    gasValueSpan.textContent = v;
    updateLevel(v);

    // Mỗi lần có điểm mới -> update prediction chart
    loadPrediction();
}

async function pollLatest() {
    try {
        const res = await fetch('/api/mq2/latest');
        const doc = await res.json();
        if (!doc || !doc.ts) return;

        if (!lastTs || doc.ts > lastTs) {
            const label = `${doc.time || ''} ${doc.date || ''}`.trim() || new Date(doc.ts).toLocaleTimeString();
            const v = Number(doc.ppm);
            appendPoint(label, Number.isFinite(v) ? v : 0);
            lastTs = doc.ts;
        }
    } catch (e) {
        console.warn('pollLatest error', e);
    }
}

async function pollLatestTemp() {
  try {
    const res = await fetch("/api/dht/latest");
    if (!res.ok) return;
    const doc = await res.json();
    const t = Number(doc?.temp);
    if (Number.isFinite(t)) {
      tempValueSpan.textContent = t.toFixed(1);
    } else {
      tempValueSpan.textContent = "--";
    }
  } catch (e) {
    console.warn("pollLatestTemp error", e);
  }
}

document.addEventListener('DOMContentLoaded', async () => {
    await fetchHistory();
    setInterval(pollLatest, 2000);

    await pollLatestTemp();         // gọi ngay 1 lần để hiện nhanh
    setInterval(pollLatestTemp, 2000);
});

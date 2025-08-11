const SOUND_URL = "/configuration/sound";
document.getElementById('sound').addEventListener('change', (e) => {
    fetch(SOUND_URL, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ sound: e.target.checked ? "ON" : "OFF" })
    }).catch(() => { e.target.checked = !e.target.checked; });
});

const YELLOWLED_URL = "/configuration/yellowled";
document.getElementById('yellowled').addEventListener('change', (e) => {
    fetch(YELLOWLED_URL, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ yellowled: e.target.checked ? "ON" : "OFF" })
    }).catch(() => { e.target.checked = !e.target.checked; });
});

const REDLED_URL = "/configuration/redled";
document.getElementById('redled').addEventListener('change', (e) => {
    fetch(REDLED_URL, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ redled: e.target.checked ? "ON" : "OFF" })
    }).catch(() => { e.target.checked = !e.target.checked; });
});
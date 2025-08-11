const SOUND_URL = "/configuration/sound";
document.getElementById('sound').addEventListener('change', (e) => {
    fetch(SOUND_URL, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ sound: e.target.checked ? "ON" : "OFF" })
    }).catch(() => { e.target.checked = !e.target.checked; });
});
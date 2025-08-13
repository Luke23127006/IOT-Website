(function () {
    // ✅ tránh khởi tạo trùng nếu file được include nhiều lần
    if (window.__offall_poll_started__) return;
    window.__offall_poll_started__ = true;

    const modal = document.getElementById("offall-modal");
    const btnConfirm = document.getElementById("offall-confirm");
    const btnCancel = document.getElementById("offall-cancel");

    let showing = false;
    let paused = false; // tạm dừng khi tab ẩn
    let sending = false; // đang gửi confirm/cancel

    function openModal() {
        modal.style.display = "block";
        modal.setAttribute("aria-hidden", "false");
        showing = true;
    }

    function closeModal() {
        modal.style.display = "none";
        modal.setAttribute("aria-hidden", "true");
        showing = false;
    }

    async function pollPing() {
        if (paused) { setTimeout(pollPing, 1000); return; }
        try {
            const res = await fetch("/api/mqtt/ping", { credentials: "same-origin" });
            const data = await res.json();
            const cmd = data && data.cmd;
            if (cmd && cmd.kind === "OFF_ALL_REQUEST" && !showing) {
                openModal();
            }
        } catch (e) {
            // bỏ qua 1 lần lỗi; sẽ thử lại
        } finally {
            setTimeout(pollPing, 2000); // poll 2s
        }
    }

    // ✅ tạm dừng poll khi tab ẩn để tiết kiệm tài nguyên
    document.addEventListener("visibilitychange", () => {
        paused = document.hidden;
    });

    btnConfirm.addEventListener("click", async () => {
        if (sending) return;
        sending = true;
        btnConfirm.disabled = true; btnCancel.disabled = true;

        try {
            const res = await fetch("/configuration/off_all_alert/confirm", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                credentials: "same-origin",
                body: JSON.stringify({})
            });
            const data = await res.json();
            if (data && data.ok) {
                // 🔄 Reload trang ngay khi xác nhận thành công
                location.reload();
                return; // phòng hờ
            } else {
                alert(data?.error || "Thao tác thất bại. Vui lòng thử lại.");
            }
        } catch (e) {
            alert("Lỗi mạng. Vui lòng thử lại.");
        } finally {
            sending = false;
            btnConfirm.disabled = false; btnCancel.disabled = false;
            closeModal();
        }
    });

    btnCancel.addEventListener("click", async () => {
        if (sending) return;
        sending = true;
        btnConfirm.disabled = true; btnCancel.disabled = true;

        try {
            await fetch("/configuration/off_all_alert/cancel", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                credentials: "same-origin",
                body: JSON.stringify({})
            });
        } finally {
            sending = false;
            btnConfirm.disabled = false; btnCancel.disabled = false;
            closeModal();
        }
    });

    // 🚀 bắt đầu poll khi trang load
    pollPing();
})();
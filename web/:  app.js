const tg = window.Telegram.WebApp;

tg.ready();
tg.expand();
fetch("/api/balance?telegram_id=" + tg.initDataUnsafe.user?.id)
    .then(response => response.json())
    .then(data => {
        document.getElementById("balance").textContent = data.balance;
    });
fetch("/api/register", {
    method: "POST",
    headers: {
        "Content-Type": "application/json"
    },
    body: JSON.stringify({
        telegram_id: tg.initDataUnsafe.user?.id
    })
});
const mineButton = document.getElementById("mineButton");

mineButton.addEventListener("click", () => {
    tg.HapticFeedback.impactOccurred("medium");

    mineButton.style.transform = "scale(0.97)";

    setTimeout(() => {
        mineButton.style.transform = "";
    }, 120);
});

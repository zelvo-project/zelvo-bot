const tg = window.Telegram.WebApp;

tg.ready();
tg.expand();
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

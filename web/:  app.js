const tg = window.Telegram.WebApp;

tg.ready();
tg.expand();

const mineButton = document.getElementById("mineButton");

mineButton.addEventListener("click", () => {
    tg.HapticFeedback.impactOccurred("medium");

    mineButton.style.transform = "scale(0.97)";

    setTimeout(() => {
        mineButton.style.transform = "";
    }, 120);
});


const tg = window.Telegram.WebApp;

tg.ready();
tg.expand();

const balanceElement = document.getElementById("balance");
const mineButton = document.getElementById("mineButton");

async function registerUser() {
    if (!tg.initData) {
        console.error("Telegram data is missing.");
        return;
    }

    try {
        const response = await fetch("/api/register", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({
                init_data: tg.initData
            })
        });

        if (!response.ok) {
            throw new Error("Registration failed: " + response.status);
        }

        await loadBalance();
    } catch (error) {
        console.error("Registration error:", error);
    }
}

async function loadBalance() {
    try {
        const response = await fetch("/api/balance", {
            headers: {
                "X-Telegram-Init-Data": tg.initData
            }
        });

        if (!response.ok) {
            throw new Error("Balance request failed: " + response.status);
        }

        const data = await response.json();
        balanceElement.textContent = data.balance;
    } catch (error) {
        console.error("Balance error:", error);
    }
}

if (balanceElement) {
    registerUser();
}

if (mineButton) {
    mineButton.addEventListener("click", () => {
        tg.HapticFeedback?.impactOccurred("medium");

        mineButton.style.transform = "scale(0.97)";

        setTimeout(() => {
            mineButton.style.transform = "";
        }, 120);
    });
}

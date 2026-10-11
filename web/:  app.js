
const tg = window.Telegram.WebApp;

tg.ready();
tg.expand();

const balanceElement = document.getElementById("balance");
const mineButton = document.getElementById("mineButton");

async function postRequest(path) {
    const response = await fetch(path, {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({
            init_data: tg.initData
        })
    });

    const data = await response.json();

    if (!response.ok) {
        throw new Error(data.message || "حدث خطأ");
    }

    return data;
}

async function loadBalance() {
    const response = await fetch("/api/balance", {
        headers: {
            "X-Telegram-Init-Data": tg.initData
        }
    });

    if (!response.ok) {
        throw new Error("تعذر تحميل الرصيد");
    }

    const data = await response.json();
    balanceElement.textContent = data.balance;
}

async function registerUser() {
    if (!tg.initData) {
        console.error("Telegram data is missing.");
        return;
    }

    try {
        await postRequest("/api/register");
        await loadBalance();
    } catch (error) {
        console.error("Registration error:", error);
    }
}

if (balanceElement) {
    registerUser();
}

if (mineButton) {
    mineButton.addEventListener("click", async () => {
        if (!tg.initData || mineButton.disabled) return;

        mineButton.disabled = true;
        tg.HapticFeedback?.impactOccurred("medium");

        try {
            const data = await postRequest("/api/mine");
            balanceElement.textContent = data.balance;
            tg.showAlert?.(`ربحت ${data.reward} ZELVO 🍃`);
        } catch (error) {
            tg.showAlert?.(error.message);
            console.error("Mining error:", error);
        } finally {
            setTimeout(() => {
                mineButton.disabled = false;
            }, 10000);
        }
    });
}

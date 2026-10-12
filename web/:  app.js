const tg = window.Telegram.WebApp;

tg.ready();
tg.expand();

const balanceElement = document.getElementById("balance");
const mineButton = document.getElementById("mineButton");

async function readResponse(response) {
    const text = await response.text();
    let data;

    try {
        data = JSON.parse(text);
    } catch {
        throw new Error(
            `استجابة غير مفهومة من السيرفر (HTTP ${response.status})`
        );
    }

    if (!response.ok) {
        throw new Error(data.message || `خطأ HTTP ${response.status}`);
    }

    return data;
}

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

    return await readResponse(response);
}

async function loadBalance() {
    const response = await fetch("/api/balance", {
        headers: {
            "X-Telegram-Init-Data": tg.initData
        }
    });

    const data = await readResponse(response);
    balanceElement.textContent = data.balance;
}

async function registerUser() {
    if (!tg.initData) {
        console.error("Telegram data is missing.");
        tg.showAlert("افتح Zelvo من داخل تيليجرام.");
        return;
    }

    try {
        await postRequest("/api/register");
        await loadBalance();
        console.log("Zelvo: تم تسجيل المستخدم وتحميل الرصيد.");
    } catch (error) {
        console.error("Registration error:", error);
        tg.showAlert("تعذّر تحميل الرصيد: " + error.message);
    }
}

if (balanceElement) {
    registerUser();
}

if (mineButton) {
    mineButton.addEventListener("click", async () => {
        if (!tg.initData) {
            tg.showAlert("افتح Zelvo من داخل تيليجرام.");
            return;
        }

        if (mineButton.disabled) {
            return;
        }

        mineButton.disabled = true;
        tg.HapticFeedback?.impactOccurred("medium");

        try {
            const data = await postRequest("/api/mine");

            if (balanceElement) {
                balanceElement.textContent = data.balance;
            }

            tg.showAlert(`ربحت ${data.reward} ZELVO 🍃`);
        } catch (error) {
            console.error("Mining error:", error);
            tg.showAlert("فشل التعدين: " + error.message);
        } finally {
            setTimeout(() => {
                mineButton.disabled = false;
            }, 10000);
        }
    });
}

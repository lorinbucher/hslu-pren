"use strict"

const actionEndpoint = "/action"
const settingsEndpoint = "/settings"
const statusEndpoint = "/status"

const homePage = document.getElementById("home");
const settingsPage = document.getElementById("settings");

const efficiencyModeInput = document.getElementById("efficiency-mode")
const fastModeInput = document.getElementById("fast-mode")
const incrementalBuildInput = document.getElementById("incremental-build")

const confidenceInput = document.getElementById("confidence");
const confidenceText = document.getElementById("confidence-value");
confidenceInput.addEventListener("input", (event) => {
    confidenceText.textContent = event.target.value + " frames";
});

const recognitionTimeoutInput = document.getElementById("recognition-timeout");
const recognitionTimeoutText = document.getElementById("recognition-timeout-value");
recognitionTimeoutInput.addEventListener("input", (event) => {
    recognitionTimeoutText.textContent = event.target.value + "s";
});

const homeButton = document.getElementById("btn-home");
homeButton.addEventListener("click", () => {
    homePage.classList.add("active");
    settingsPage.classList.remove("active");
});

const initButton = document.getElementById("btn-init");
initButton.addEventListener("click", () => {
    sendPostRequest(actionEndpoint, {"action": "init"}).then();
});

const startButton = document.getElementById("btn-start");
startButton.addEventListener("click", () => {
    sendPostRequest(actionEndpoint, {"action": "start"}).then();
});

const pauseButton = document.getElementById("btn-pause");
pauseButton.addEventListener("click", () => {
    sendPostRequest(actionEndpoint, {"action": "stop"}).then();
});

const settingsButton = document.getElementById("btn-settings");
settingsButton.addEventListener("click", () => {
    settingsPage.classList.add("active");
    homePage.classList.remove("active");
    sendGetRequest(settingsEndpoint)
        .then(data => {
            const {efficiency_mode, fast_mode, incremental_build, confidence, recognition_timeout} = data;
            efficiencyModeInput.checked = efficiency_mode || false;
            fastModeInput.checked = fast_mode || false;
            incrementalBuildInput.checked = incremental_build || false;
            confidenceInput.value = confidence || 25;
            confidenceText.textContent = confidenceInput.value + " frames";
            recognitionTimeoutInput.value = recognition_timeout || 180;
            recognitionTimeoutText.textContent = recognitionTimeoutInput.value + "s";
        });
});

const saveButton = document.getElementById("btn-save");
saveButton.addEventListener("click", () => {
    sendPostRequest(settingsEndpoint, {
        "efficiency_mode": efficiencyModeInput.checked,
        "fast_mode": fastModeInput.checked,
        "incremental_build": incrementalBuildInput.checked,
        "confidence": parseInt(confidenceInput.value),
        "recognition_timeout": parseInt(recognitionTimeoutInput.value, 10)
    }).then();
});

const restartButton = document.getElementById("btn-restart");
restartButton.addEventListener("click", () => {
    sendPostRequest(actionEndpoint, {"action": "restart"}).then();
});

const rebootButton = document.getElementById("btn-reboot");
rebootButton.addEventListener("click", () => {
    sendPostRequest(actionEndpoint, {"action": "reboot"}).then();
});

const resetButton = document.getElementById("btn-reset");
resetButton.addEventListener("click", () => {
    sendPostRequest(actionEndpoint, {"action": "reset"}).then();
});

// HTTP Requests
async function sendGetRequest(url) {
    try {
        const response = await fetch(url);
        if (!response.ok) {
            console.error("Request failed: ", response.status, await response.text());
            return undefined
        }
        return await response.json();
    } catch (error) {
        console.error("Error fetching data:", error);
    }
}

async function sendPostRequest(url, data) {
    try {
        const response = await fetch(url, {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify(data)
        });

        const responseText = await response.text()
        if (!response.ok) {
            console.error("Request failed: ", response.status, responseText);
        }
        return responseText;
    } catch (error) {
        console.error("Error fetching data:", error);
    }
}

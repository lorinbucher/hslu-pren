"use strict"

const actionEndpoint = "/action"
const settingsEndpoint = "/settings"
const statusEndpoint = "/status"

const pollingInterval = 1000;
let statusFetchTask = setInterval(fetchStatus, pollingInterval);

const formatter = new Intl.NumberFormat("de-ch", {
    minimumFractionDigits: 3,
    maximumFractionDigits: 3
});

// Home Page
const homePage = document.getElementById("home");
const cubeElements = document.querySelectorAll('[id^="cube-"]');
const statusText = document.getElementById("status-value");
const startTimeText = document.getElementById("start-time-value");
const configTimeText = document.getElementById("config-time-value");
const endTimeText = document.getElementById("end-time-value");
const energyText = document.getElementById("energy-value");
const progressText = document.getElementById("build-progress-value");
const progressBar = document.getElementById("build-progress")

const homeButton = document.getElementById("btn-home");
homeButton.addEventListener("click", () => {
    homePage.classList.add("active");
    settingsPage.classList.remove("active");
    statusFetchTask = setInterval(fetchStatus, pollingInterval);
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

// Settings Page
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

const settingsButton = document.getElementById("btn-settings");
settingsButton.addEventListener("click", () => {
    settingsPage.classList.add("active");
    homePage.classList.remove("active");
    clearInterval(statusFetchTask);
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

// App

// TODO: handle config

async function fetchStatus() {
    sendGetRequest(statusEndpoint)
        .then(data => {
            const {config, energy, status, steps_finished, steps_total, time_config, time_end, time_start} = data;
            let startDate;
            if (time_start) {
                startDate = new Date(time_start / 1e6).toLocaleTimeString('de-ch')
            }
            const startToConfig = Math.max(0, (time_config - time_start) / 1e9);
            const startToEnd = Math.max(0, (time_end - time_start) / 1e9);

            updateButtonState(status);
            updateConfigState(config);

            statusText.textContent = status || "idle";
            startTimeText.textContent = startDate || "00:00:00";
            configTimeText.textContent = formatter.format(startToConfig || 0) + "s";
            endTimeText.textContent = formatter.format(startToEnd || 0) + "s";
            energyText.textContent = formatter.format(energy || 0) + " Wh";
            progressText.textContent = (Math.ceil((100 / steps_total) * steps_finished) || "0") + "%";
            progressBar.max = steps_total || 0;
            progressBar.value = steps_finished || 0;
        });
}

function updateButtonState(status) {
    switch (status) {
        case "ready":
            initButton.disabled = true;
            startButton.disabled = false
            pauseButton.disabled = true;
            break;
        case "running":
            initButton.disabled = true;
            startButton.disabled = true;
            pauseButton.disabled = false
            break;
        case "paused":
            initButton.disabled = true;
            startButton.disabled = false
            pauseButton.disabled = true;
            break;
        default:
            initButton.disabled = false
            startButton.disabled = true;
            pauseButton.disabled = true;
            break;
    }
}

function updateConfigState(config) {
    cubeElements.forEach(cube => {
        const index = parseInt(cube.id.replace('cube-', ''), 10);
        const color = config[index - 1] || "none";
        cube.classList.remove("unknown", "none", "red", "yellow", "blue");
        cube.classList.add(color);
    });
}

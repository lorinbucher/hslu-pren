"use strict"

// Navigation
const homeButton = document.getElementById('btn-home');
const settingsButton = document.getElementById('btn-settings');
const homePage = document.getElementById('home');
const settingsPage = document.getElementById('settings');

homeButton.addEventListener('click', () => {
    homePage.classList.add('active');
    settingsPage.classList.remove('active');
});

settingsButton.addEventListener('click', () => {
    settingsPage.classList.add('active');
    homePage.classList.remove('active');
});

// Settings
const confidenceSlider = document.getElementById("confidence");
const recognitionTimeoutSlider = document.getElementById("recognition-timeout");
const confidenceValue = document.getElementById("confidence-value");
const recognitionTimeoutValue = document.getElementById("recognition-timeout-value");

updateSliderValue(confidenceSlider, confidenceValue, " frames");
updateSliderValue(recognitionTimeoutSlider, recognitionTimeoutValue, "s");

// Functions
function updateSliderValue(slider, valueDisplay, unit = "") {
    slider.addEventListener("input", (event) => {
        valueDisplay.textContent = event.target.value + unit;
    });
}

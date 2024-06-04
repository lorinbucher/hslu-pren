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

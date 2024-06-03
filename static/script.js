function toggleSettings() {
    var container = document.querySelector('.container');
    var settingsButtons = document.querySelector('.settings-buttons');
    var settings = document.querySelector('.settings');
    var controls = document.querySelector('.controls');

    if (container.style.display === 'none') {
        container.style.display = 'block';
        settings.style.display = 'none';
        settingsButtons.style.display = 'none';
        controls.style.display = 'flex';
    } else {
        container.style.display = 'none';
        settings.style.display = 'block';
        settingsButtons.style.display = 'flex';
        controls.style.display = 'none';
    }
}

function changeColor(button) {
    var colors = ["red", "yellow", "blue", "white"];
    var currentIndex = colors.indexOf(button.style.backgroundColor);
    var newIndex = (currentIndex + 1) % colors.length;
    button.style.backgroundColor = colors[newIndex];
}
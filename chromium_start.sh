#!/usr/bin/env bash
# Auto start the chromium browser fullscreen and in kiosk mode.

/usr/bin/chromium-browser --app=http://localhost:5000/index.html --start-fullscreen --kiosk

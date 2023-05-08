#!/bin/bash

xset s noblank
xset s off
xset -dpms
export DISPLAY=:0.0

unclutter -idle 0.5 -root &

sed -i 's/"exited_cleanly":false/"exited_cleanly":true/' /home/pi/.config/chromium/Default/Preferences
sed -i 's/"exit_type":"Crashed"/"exit_type":"Normal"/' /home/pi/.config/chromium/Default/Preferences

/usr/bin/chromium-browser --noerrdialogs --disable-infobars --kiosk http://127.0.0.0:80/scoreboard  &

while true; do
   #xdotool keydown ctrl+Tab; xdotool keyup ctrl+Tab;
   sleep 10
done

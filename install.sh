
sudo apt update
sudo apt full-upgrade
sudo apt install xdotool unclutter
sudo rm /etc/xdg/autostart/piwiz.desktop
sudo apt-get install git
git clone https://github.com/roocell/scoreboard.git

sudo apt-get install python3-pip
sudo pip3 install flask
sudo pip3 install flask-socketio
sudo pip3 install eventlet
sudo cp -f ~/scoreboard/scoreboard.service /etc/systemd/system/
sudo cp -f ~/scoreboard/kiosk.service /lib/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable scoreboard
sudo systemctl start scoreboard
sudo systemctl enable kiosk.service
sudo systemctl start kiosk.service

sudo apt-get install hostapd
sudo apt-get install dnsmasq
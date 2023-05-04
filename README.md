# scoreboard
scoreboard running on raspi. 

<<<<<<< Updated upstream
# start with piOs 32-bit desktop and 'pi' user
# use raspi imager, use CTRL-SHIFT-X to setup SSH and wifi

# login and update
```
sudo apt update
sudo apt full-upgrade

```

# auto login for desktop
```
sudo apt install xdotool unclutter
sudo rm /etc/xdg/autostart/piwiz.desktop
```

# change config to automatically login as pi user for desktop
```
sudo raspi-config
system->desktop autologin->Finish->reboot
```

# install git and download scoreboard code
# install scoreboard things
```
sudo apt-get install git
git clone https://github.com/roocell/scoreboard.git

sudo apt-get install python3-pip
sudo pip3 install flask
sudo pip3 install flask-socketio
sudo pip3 install eventlet
sudo cp -f ~/scoreboard/scoreboard.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable scoreboard
sudo systemctl start scoreboard
```

# for development (skip if not developing)
# install samba and store git creds
```
sudo apt-get install samba samba-common-bin
sudo echo -e "[pi]\npath = /home/pi/\nwriteable=Yes\ncreate mask=0777\ndirectory mask=0777\npublic=no\nmangled names = no" >>  /etc/samba/smb.conf
```

```
sudo smbpasswd -a pi
sudo systemctl restart smbd
cd scoreboard
git config credential.helper store
git config --global user.email "roocell@gmail.com"
git config --global user.name "Michael Russell"

```

# start manually (rather than service) (dev)
sudo systemctl disable scoreboard
sudo python3 app.py

# setup kiosk mode
This will allow us to display just a webpage on the video out.
And we don't have to install the entire desktop piOs image.
from https://www.raspberrypi.com/tutorials/how-to-use-a-raspberry-pi-in-kiosk-mode/
```
sudo cp -f ~/scoreboard/kiosk.service /lib/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable kiosk.service
sudo systemctl start kiosk.service
```

# to restart kiosk webpage
```
sudo systemctl restart kiosk.service
sudo systemctl restart scoreboard.service
```

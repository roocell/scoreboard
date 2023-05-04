# scoreboard
scoreboard running on raspi. 

# start with piOs 32-bit desktop
# use raspi imager, use CTRL-SHIFT-X to setup SSH and wifi

# login and update
```
sudo apt update
sudo apt full-upgrade
```

# auto login for desktop
```
sudo apt install xdotool unclutter
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
```

# for development (skip if not developing)
# install samba and store git creds
```
sudo apt-get install samba samba-common-bin
sudo vi /etc/samba/smb.conf
```
```
[pi]
path = /home/pi/
writeable=Yes
create mask=0777
directory mask=0777
public=no
mangled names = no
```
```
sudo smbpasswd -a pi
sudo systemctl restart smbd
cd scoreboard
git config credential.helper store
```

# setup kiosk mode
This will allow us to display just a webpage on the video out.
And we don't have to install the entire desktop piOs image.
from https://www.raspberrypi.com/tutorials/how-to-use-a-raspberry-pi-in-kiosk-mode/
```
cp -f ~/scoreboard/kiosk.sh ~
sudo cp -f ~/scoreboard/kiosk.service /lib/systemd/system/
sudo systemctl enable kiosk.service
sudo systemctl start kiosk.service
```

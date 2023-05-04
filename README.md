# scoreboard
scoreboard running on raspi. 

# start with piOs lite (latest)
```
sudo apt-get update
sudo apt-get upgrade

sudo apt-get install git
git clone https://github.com/roocell/scoreboard.git
git config credential.helper store

sudo apt-get install python3-pip
sudo pip3 install flask
sudo pip3 install flask-socketio
```

# samba for remote dev via mapped drive
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
```

# raspi in kiosk mode
This will allow us to display just a webpage on the video out.
And we don't have to install the entire desktop piOs image.
https://www.raspberrypi.com/tutorials/how-to-use-a-raspberry-pi-in-kiosk-mode/

```
sudo apt install xdotool unclutter
```

# change config to automatically login as pi user for desktop
# (so we don't have to login)
```
sudo raspi-config
sudo apt-get install lightdm
sudo reboot
```

# copy over kiosk files
```
cp -f ~/scoreboard/kiosk.sh ~
sudo cp -f ~/scoreboard/kiosk.service /lib/systemd/system/
sudo systemctl enable kiosk.service
sudo systemctl start kiosk.service
```
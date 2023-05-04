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

# install and start Wifi Access Point
https://pimylifeup.com/raspberry-pi-wireless-access-point/

```
sudo apt install hostapd dnsmasq iptables
sudo echo -e "interface wlan0\n  static ip_address=192.168.0.10/24\n  nohook wpa_supplicant" >> /etc/dhcpcd.conf
sudo mv /etc/dnsmasq.conf /etc/dnsmasq.conf.orig
sudo bash -c 'echo -e "interface=wlan0\n  dhcp-range=192.168.0.11,192.168.0.30,255.255.255.0,24h\n" > /etc/dnsmasq.conf'

sudo bash -c 'echo -e "interface=wlan0\ndriver=nl80211\nieee80211n=1\n#bridge=br0\nhw_mode=g\nchannel=7\nwmm_enabled=0\nmacaddr_acl=0\nauth_algs=1\nignore_broadcast_ssid=0\nwpa=2\nwpa_key_mgmt=WPA-PSK\nwpa_pairwise=TKIP\nrsn_pairwise=CCMP\nssid=scoreboard\nwpa_passphrase=12345678" > /etc/hostapd/hostapd.conf'
sudo mv /etc/default/hostapd /etc/default/hostapd.old
sudo bash -c  "sed  's/.*DAEMON_CONF.*/DAEMON_CONF=\"\/etc\/hostapd\/hostapd.conf\"/'  /etc/default/hostapd.old >>  /etc/default/hostapd"

sudo mv /etc/sysctl.conf /etc/sysctl.conf.old
sudo bash -c "sed 's/.*net.ipv4.ip_forward.*/net.ipv4.ip_forward=1/' /etc/sysctl.conf.old > /etc/sysctl.conf"

sudo iptables -t nat -A POSTROUTING -o eth0 -j MASQUERADE
sudo sh -c "iptables-save > /etc/iptables.ipv4.nat"
sudo iptables-restore < /etc/iptables.ipv4.nat
sudo apt-get install bridge-utils
sudo brctl addbr br0
sudo brctl addif br0 eth0
sudo bash -c 'echo -e "auto br0\niface br0 inet manual\nbridge_ports eth0 wlan0"  >> /etc/network/interfaces'

sudo systemctl unmask hostapd
sudo systemctl enable hostapd
sudo systemctl start hostapd

```

# captive portal
https://pimylifeup.com/raspberry-pi-captive-portal/

sudo apt install git libmicrohttpd-dev build-essential
cd ~
git clone https://github.com/nodogsplash/nodogsplash.git
cd ~/nodogsplash
make
sudo make install

sudo cp /etc/nodogsplash/nodogsplash.conf /etc/nodogsplash/nodogsplash.conf.old
sudo bash -c "sed 's/.*GatewayInterface.*/GatewayInterface wlan0/' /etc/nodogsplash/nodogsplash.conf.old > /etc/nodogsplash/nodogsplash.tmp"
sudo bash -c "sed 's/.*GatewayAddress.*/GatewayAddress 192.168.1.10/' /etc/nodogsplash/nodogsplash.tmp > /etc/nodogsplash/nodogsplash.tmp2"
sudo bash -c "sed 's/.*AuthIdleTimeout.*/AuthIdleTimeout 600/' /etc/nodogsplash/nodogsplash.tmp2 > /etc/nodogsplash/nodogsplash.conf"

sudo cp -f /etc/rc.local /etc/rc.local.old
sudo bash -c "sed 's/.*exit 0.*/nodogsplash\nexit 0\' /etc/rc.local.old > /etc/rc.local"

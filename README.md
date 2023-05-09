# scoreboard
scoreboard running on raspi.
Intended to be used with a projector using HDMI, controlled via wifi using a phone/tablet.

# simple install and instructions
Start with piOs 32-bit desktop with a 'pi' user.<BR>
This app sets up wifi0 and uses it to function.<BR>
So this must be installed by<BR>
  <li>desktop interface or</li>
  <li>SSH over wifi1</li>
  <BR>
  
```
wget https://raw.githubusercontent.com/roocell/scoreboard/main/install.sh
chmod 777 install.sh
sudo ./install.sh
sudo reboot
```
Connect raspi to projector.<BR>
Connect phone/tablet to wifi. Network: <b>scoreboard</b> password: <b>12345678</b><BR>
Once connected over wifi on your phone/tablet, open a browser to http://scoreboard<BR>

<img src="/scoreboard.jpg" alt="scoreboard" width="500" height="300">
<img src="/controller.jpg" alt="controller" width="500" height="300">

# if you need a different subnet than 192.168.0.X to get internet access
edit these 3 files. changing 192.168.0 to a different subnet (like 192.168.30)
```
/etc/dhcpcd.conf
/etc/dnsmasq.conf
/etc/hosts
```
and then reboot

# to update
```
cd /home/pi/scoreboard
git pull
sudo systemctl restart scoreboard
sudo systemctl restart kiosk
```

# detailed manual install / notes
Start with piOs 32-bit desktop and 'pi' user
Use raspi imager, use CTRL-SHIFT-X to setup SSH and wifi

### login and update
```
sudo apt update
sudo apt full-upgrade

```

### auto login for desktop
```
sudo apt install xdotool unclutter
sudo rm /etc/xdg/autostart/piwiz.desktop
```

### change config to automatically login as pi user for desktop
```
sudo raspi-config
system->boot/autologin->desktop autologin->Finish->reboot

or by command line
sudo cp -f /etc/lightdm/lightdm.conf /etc/lightdm/lightdm.conf.old
sudo bash -c  "sed  's/.*autologin-user=.*/autologin-user=pi/' /etc/lightdm/lightdm.conf.old > /etc/lightdm/lightdm.conf.tmp"
sudo bash -c  "sed  's/.*autologin-user-timeout=.*/autologin-user-timeout=0/' /etc/lightdm/lightdm.conf.tmp > /etc/lightdm/lightdm.conf"


```

### install git and download scoreboard code
Install scoreboard things
flask-socketio needs to be updated - so have to revert to python-socketio==5.7.2
```
sudo apt-get install git
git clone https://github.com/roocell/scoreboard.git

sudo apt-get install python3-pip
sudo pip3 install flask
sudo pip3 install flask-socketio
sudo pip3 install eventlet

sudo pip3 uninstall python-socketio
sudo pip3 install python-socketio==5.7.2

sudo cp -f ~/scoreboard/scoreboard.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable scoreboard
sudo systemctl start scoreboard
```

### install samba and store git creds
for development (skip if not developing)
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

### setup kiosk mode
This will allow us to display just a webpage on the video out.
And we don't have to install the entire desktop piOs image.
from https://www.raspberrypi.com/tutorials/how-to-use-a-raspberry-pi-in-kiosk-mode/
```
sudo cp -f ~/scoreboard/kiosk.service /lib/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable kiosk.service
sudo systemctl start kiosk.service
```

### to restart kiosk webpage (dev)
```
sudo systemctl restart kiosk.service
sudo systemctl restart scoreboard.service
```

### start manually (rather than service) (dev)
sudo systemctl disable scoreboard
cd scoreboard
sudo python3 app.py


### install and start Wifi Access Point
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

### captive portal (optional)
https://pimylifeup.com/raspberry-pi-captive-portal/
seems kind of flaky - maybe better just to use a hostname

```
sudo apt install git libmicrohttpd-dev build-essential
cd /home/pi
git clone https://github.com/nodogsplash/nodogsplash.git
cd /home/pi/nodogsplash
make
sudo make install

sudo cp /etc/nodogsplash/nodogsplash.conf /etc/nodogsplash/nodogsplash.conf.old
sudo bash -c "sed 's/.*GatewayInterface.*/GatewayInterface wlan0/' /etc/nodogsplash/nodogsplash.conf.old > /etc/nodogsplash/nodogsplash.tmp"
sudo bash -c "sed 's/.*GatewayAddress.*/GatewayAddress 192.168.1.10/' /etc/nodogsplash/nodogsplash.tmp > /etc/nodogsplash/nodogsplash.tmp2"
sudo bash -c "sed 's/.*AuthIdleTimeout.*/AuthIdleTimeout 600/' /etc/nodogsplash/nodogsplash.tmp2 > /etc/nodogsplash/nodogsplash.conf"

sudo cp -f /etc/rc.local /etc/rc.local.old
sudo bash -c "sed 's/.*exit 0.*/nodogsplash\nexit 0\' /etc/rc.local.old > /etc/rc.local"

sudo bash -c "echo -e 'SplashPage http://scoreboard' >> /etc/nodogsplash/nodogsplash.conf"
```

### hostname  
https://pimylifeup.com/raspberry-pi-hostname/#:~:text=A%20hostname%20is%20a%20human,mac%20address%20of%20each%20device.

```
sudo bash -c 'echo -e "192.168.0.10 scoreboard" >> /etc/hosts'
```

### eventlet, socketio, threads and monkeypatch
This monkeypatch is required if you want to emit() from a thread.
We want to do this to update the clock.

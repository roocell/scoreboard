
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

# wifi AP
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

# scoreboard host
sudo bash -c 'echo -e "192.168.0.10 scoreboard" >> /etc/hosts'
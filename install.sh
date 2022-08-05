#!/bin/bash

if [[ $UID != '0' ]]
then
	echo Script must be run as root
	exit 1
fi

PATH_CONF=/etc/stream.cfg
PATH_EDID=/etc/720p60.bin
PATH_INIT=/usr/bin/init-hdmi.sh
PATH_STREAM=/usr/bin/stream.py
PATH_SERVICE=/etc/systemd/system/streamer.service
PATH_BT_SVC=/lib/systemd/system/bluetooth.service
PATH_RFCOMM_SVC=/etc/systemd/system/rfcomm.service
PATH_WIFI_SVC=/etc/systemd/system/wifi-powersave-off.service

apt install -y gstreamer1.0-tools gstreamer1.0-plugins-{good,bad,ugly} python3-pip
pip install -r requirements.txt

cp -f stream.cfg $PATH_CONF
cp -f 720p60.bin $PATH_EDID
cp -f init-hdmi.sh $PATH_INIT
cp -f stream.py $PATH_STREAM
cp -f streamer.service $PATH_SERVICE
cp -f bluetooth.service $PATH_BT_SVC
cp -f rfcomm.service $PATH_RFCOMM_SVC
cp -f wifi-powersave-off.service $PATH_WIFI_SVC

systemctl daemon-reload
systemctl enable bluetooth.service
systemctl enable rfcomm.service
systemctl enable streamer.service
systemctl enable wifi-powersave-off.service

echo Ready!

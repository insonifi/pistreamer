#!/bin/bash

if [[ $UID != '0' ]]
then
	echo Script must be run as root
	exit 1
fi

TKEY_HOLDER=__TKEY__
PATH_EDID=/etc/720p60.bin
PATH_INIT=/usr/bin/init-hdmi.sh
PATH_STREAM=/usr/bin/stream.py
PATH_SERVICE=/etc/systemd/system/streamer.service
PATH_WIFI_SVC=/etc/systemd/system/wifi-powersave-off.service
TKEY=`sed -En 's/^.*TWITCH_KEY=([[:alnum:]]+)/\1/p'  $PATH_SERVICE`

cp -f 720p60.bin $PATH_EDID
cp -f init-hdmi.sh $PATH_INIT
cp -f stream.py $PATH_STREAM
cp -f streamer.service $PATH_SERVICE
cp -f wifi-powersave-off.service $PATH_WIFI_SVC

if [[ $TKEY == '' ]]
then
	echo -n Enter a Twitch key: 
	read TKEY
fi

sed -e s/$TKEY_HOLDER/$TKEY/ -i $PATH_SERVICE

systemctl daemon-reload
systemctl enable streamer.service
systemctl enable wifi-powersave-off.service

echo Ready!

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

ln -fs 720p60.bin $PATH_EDID
ln -fs init-hdmi.sh $PATH_INIT
ln -fs stream.py $PATH_STREAM
cp -f streamer.service $PATH_SERVICE

if [[ `sed -n /$TKEY_HOLDER/p $PATH_SERVICE` != '' ]]
then
	echo -n Enter a Twitch key:
	read TKEY
	sed -e s/$TKEY_HOLDER/$TKEY/ -i $PATH_SERVICE
fi

systemctl daemon-reload
systemctl enable streamer.service

echo Ready!

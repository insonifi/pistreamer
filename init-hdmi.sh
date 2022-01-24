#!/bin/bash

v4l2-ctl --set-edid=file=/etc/720p60.bin --fix-edid-checksum
v4l2-ctl -v pixelformat=UYVY
v4l2-ctl --set-dv-bt-timings query
v4l2-ctl --log-status

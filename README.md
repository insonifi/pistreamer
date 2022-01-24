# pistreamer

Pi Zero W  with a HDMI to CSI bridge that streams input to Twitch

- **720p60.bin** -- EDID for 1280x720 @ 60fps video input
- **init-hdmi.sh** -- initialises TC358743 HDMI to CSI-2 bridge: loads EDID and queries timings of the connected source
- **stream.py** -- grabs, encodes and pushes the stream to Twitch
- **streamer.service** -- systemd service to manage streaming

# Install

```
bash install.sh
```

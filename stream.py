#!/usr/bin/env python3

'''
Simple example to demonstrate dynamically adding and removing source elements
to a playing pipeline.
'''

from configparser import ConfigParser
import random
import requests
import sys
from urllib.parse import urlparse

import gi
gi.require_version('Gst', '1.0')
gi.require_version('GLib', '2.0')
gi.require_version('GObject', '2.0')
from gi.repository import GLib, GObject, Gst

API_INGEST = "https://ingest.twitch.tv/ingests"
ingests = None
current_ingest = 0
config = ConfigParser()
config.read("stream.cfg")

def bus_call(bus, message, loop):
    t = message.type
    if t == Gst.MessageType.EOS:
        sys.stdout.write("End-of-stream\n")
        loop.quit()
    elif t == Gst.MessageType.ERROR:
        err, debug = message.parse_error()
        sys.stderr.write("Error: %s: %s\n" % (err, debug))
        loop.quit()
    return True

def fetch_ingests():
    global current_ingest
    global ingests

    res = requests.get(API_INGEST)

    if res.status_code != 200:
        print("Error: %s" %res.status_code)
        sys.exit(1)

    ingests = res.json()['ingests']
    current_ingest = 0



def choose_ingest():
    if ingests is None:
        fetch_ingests()

    return ingests[current_ingest]['url_template']

def main(args):
    url = choose_ingest().format(stream_key=config.get('MAIN', 'key'))

    Gst.init(None)

    caps_video = Gst.Caps.from_string('video/x-raw,framerate=60/1,format=UYVY')
    caps_stream = Gst.Caps.from_string('video/x-h264,level=(string)4')

    pipe = Gst.Pipeline.new('pipeline')
    # video = Gst.ElementFactory.make('v4l2src')
    video = Gst.ElementFactory.make('videotestsrc')
    videofilter = Gst.ElementFactory.make('capsfilter')
    # encoder = Gst.ElementFactory.make('v4l2h264enc')
    encoder = Gst.ElementFactory.make('x264enc')
    streamfilter = Gst.ElementFactory.make('capsfilter')
    parse = Gst.ElementFactory.make('h264parse')
    muxer = Gst.ElementFactory.make('flvmux')
    sink = Gst.ElementFactory.make('rtmpsink')

    videofilter.set_property('caps', caps_video)
    streamfilter.set_property('caps', caps_stream)
    sink.set_property('location', get_url())

    pipe.add(video)
    pipe.add(videofilter)
    pipe.add(encoder)
    pipe.add(streamfilter)
    pipe.add(parse)
    pipe.add(muxer)
    pipe.add(sink)

    video.link(videofilter)
    videofilter.link(encoder)
    encoder.link(streamfilter)
    streamfilter.link(parse)
    parse.link(muxer)
    muxer.link(sink)

    loop = GLib.MainLoop()

    bus = pipe.get_bus()
    bus.add_signal_watch()
    bus.connect ("message", bus_call, loop)
    
    # start play back and listen to events
    pipe.set_state(Gst.State.PLAYING)
    try:
      loop.run()
    except:
      pass
    
    # cleanup
    pipe.set_state(Gst.State.NULL)

if __name__ == '__main__':
    sys.exit(main(sys.argv))


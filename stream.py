#!/usr/bin/env python3

'''
Simple example to demonstrate dynamically adding and removing source elements
to a playing pipeline.
'''

import argparse
from configparser import ConfigParser
import os
import random
import requests
import sys
from urllib.parse import urlparse

import gi
gi.require_version('Gst', '1.0')
gi.require_version('GLib', '2.0')
gi.require_version('GObject', '2.0')
from gi.repository import GLib, GObject, Gst

argpar = argparse.ArgumentParser(description='Grab, encode and stream video from connected camera')
argpar.add_argument('--conf', dest='CONF_PATH', help='Path to the configuration file with a key', required=True)
args = argpar.parse_args()

API_INGEST = "https://ingest.twitch.tv/ingests"
ingests = None
current_ingest = 0
config = ConfigParser()
config.read(args.CONF_PATH)

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
    video = Gst.ElementFactory.make('v4l2src')
    videofilter = Gst.ElementFactory.make('capsfilter')
    encoder = Gst.ElementFactory.make('v4l2h264enc')
    streamfilter = Gst.ElementFactory.make('capsfilter')
    parse = Gst.ElementFactory.make('h264parse')
    queue = Gst.ElementFactory.make('queue')
    muxer = Gst.ElementFactory.make('flvmux')
    sink = Gst.ElementFactory.make('rtmpsink')

    videofilter.set_property('caps', caps_video)
    streamfilter.set_property('caps', caps_stream)
    parse.set_property('config-interval', -1)
    muxer.set_property('streamable', True)
    sink.set_property('location', url)

    pipe.add(video)
    pipe.add(videofilter)
    pipe.add(encoder)
    pipe.add(streamfilter)
    pipe.add(parse)
    pipe.add(queue)
    pipe.add(muxer)
    pipe.add(sink)

    video.link(videofilter)
    videofilter.link(encoder)
    encoder.link(streamfilter)
    streamfilter.link(parse)
    parse.link(muxer)
    muxer.link(queue)
    queue.link(sink)

    loop = GLib.MainLoop()

    bus = pipe.get_bus()
    bus.add_signal_watch()
    bus.connect ("message", bus_call, loop)
    
    # start play back and listen to events
    pipe.set_state(Gst.State.PLAYING)
    try:
      loop.run()
      print('Streaming…')
    except:
      print('Failed to start')
      pass
    
    # cleanup
    pipe.set_state(Gst.State.NULL)

if __name__ == '__main__':
    sys.exit(main(sys.argv))


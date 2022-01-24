#!/usr/bin/env python3

'''
Simple example to demonstrate dynamically adding and removing source elements
to a playing pipeline.
'''

import os
import random
import sys

import gi
gi.require_version('Gst', '1.0')
gi.require_version('GLib', '2.0')
gi.require_version('GObject', '2.0')
from gi.repository import GLib, GObject, Gst

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

def get_url():
    host = 'fra02'
    key = os.environ['TWITCH_KEY']
    url = 'rtmp://{host}.contribute.live-video.net/app/{key}'.format(**locals())

    return url

def main(args):
    Gst.init(None)

    caps_video = Gst.Caps.from_string('video/x-raw,framerate=60/1,format=UYVY')
    caps_stream = Gst.Caps.from_string('video/x-h264,level=(string)4')

    pipe = Gst.Pipeline.new('pipeline')
    video = Gst.ElementFactory.make('v4l2src')
    videofilter = Gst.ElementFactory.make('capsfilter')
    encoder = Gst.ElementFactory.make('v4l2h264enc')
    streamfilter = Gst.ElementFactory.make('capsfilter')
    parse = Gst.ElementFactory.make('h264parse')
    muxer = Gst.ElementFactory.make('flvmux')
    sink = Gst.ElementFactory.make('rtmpsink')

    videofilter.set_property('caps', caps_video)
    streamfilter.set_property('caps', caps_stream)
    sink.set_property('location', get_url())

    pipe.add(video, videofilter, encoder, streamfilter, parse, muxer, sink)
    Gst.Element.link_many(video, videofilter, encoder, streamfilter, parse, muxer, sink)

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


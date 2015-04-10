#!/usr/bin/env python
# -*- coding: utf-8 -*-

#########################################################################
# Author: Zhaoting Weng
# Created Time: Mon 23 Mar 2015 11:53:53 PM CST
# File Name: /tmp/main.py
# Description:
#########################################################################

from audiostream import get_input, get_output, get_input_sources, AudioSample
import time
import wave
import threading
import binascii

from kivy.app import App
from kivy.uix.button import Button
from kivy.uix.widget import Widget
from kivy.properties import ObjectProperty


class Button_Speak(Button):

    def __init__(self, **kargs):
        self.stream = get_output(channels=1, buffersize=1024, rate=8000)
        self.sample = AudioSample()
        self.stream.add_sample(self.sample)
        super(Button_Speak, self).__init__(**kargs)

    def speak(self, str_bin_data):
        self.sample.stop()
        self.sample.play()
        self.sample.write(str_bin_data)

class Button_Record(Button):

    def __init__(self, **kargs):
        self.stop_flag = {"flag": False}
        self.is_stop = False
        self.dataset = None
        super(Button_Record, self).__init__(**kargs)

    def keep_record(self, stop_flag, channels=1, encoding=16, rate=8000):

        def mic_callback(buf):
            print "got data", len(buf)
            frames.append(buf)

        frames = []
        # Need to set buffersize
        print "keep_record: Prepare..."
        mic = get_input(callback=mic_callback, channels=channels, encoding=encoding, rate=rate, buffersize = 1024)
        print "keep_record: Starting..."
        mic.start()
        print "keep_record: Started..."
        while not stop_flag["flag"]:
            # Read the internal queue and dispatch the data through the callback
            mic.poll()

        mic.stop()

        # Remove the prepending Inpulse voice
        str_bin_data = ''.join(frames)[200:]
        data = [int(binascii.b2a_hex(i), 16) for i in str_bin_data]
        return (data, str_bin_data)

    def start_record(self):
        def t_start_record():
            print "Recording..."
            self.dataset = self.keep_record(self.stop_flag)
            self.is_stop = True
        t = threading.Thread(target = t_start_record)
        print "Start record..."
        t.start()
        return self.dataset

    def stop_record(self):
        self.stop_flag["flag"] = True
        print "Stopping record..."
        while not self.is_stop:
            pass
        print "Stopped record..."
        # Prepare for next lifecycle
        self.is_stop = False
        self.stop_flag["flag"] = False


class MyWidget(Widget):
    recorder = ObjectProperty(None)
    speaker = ObjectProperty(None)

    def __init__(self, **kargs):
        self.dataset = ([], '')
        super(MyWidget, self).__init__(**kargs)

    def record(self):
        self.dataset = self.recorder.start_record()

    def stop_record(self):
        self.recorder.stop_record()

    def speak(self):
        self.speaker.speak(self.dataset[1])


class MyApp(App):

    def __init__(self, **kargs):
        super(MyApp, self).__init__(**kargs)
    def build(self):
        return MyWidget()

if __name__ == "__main__":
    MyApp().run()



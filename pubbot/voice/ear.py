# Copyright 2014 the original author or authors
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# https://pythonism.wordpress.com/tag/pyaudio/
# http://cmusphinx.sourceforge.net/wiki/gstreamer

import audioop
import collections
import logging
import tempfile

import pyaudio
import wave


class Device(object):

    def __init__(self):
        self.device = None

    def __enter__(self):
        self.device = pyaudio.PyAudio()

    def __exit__(self, *exc_info):
        if self.device:
            self.device.terminate()
            self.device = None

    def stream(self):
        if not self.device:
            raise RuntimeError("Cannot open a stream as no device open")
        return Stream(self)


class Stream(object):

    """ PyAudio abstraction for reading wav files from a device """

    def __init__(self, device):
        self.device = device
        self.stream = None

        self.rate = 16000
        self.frames_per_buffer = 1024
        #FIXME: What are the units of rate / frames_per_buffer
        self.period = self.rate / self.frames_per_buffer

        self.logger = logging.getLogger(self.__class__.__name__)

    def __enter__(self):
        if self.stream:
            raise RuntimeError("Stream already open")
        self.stream = self.device.device.open(
            format=pyaudio.paInt16,
            channels=1,
            rate=self.rate,
            frames_per_buffer=self.frames_per_buffer,
            input=True,
        )
        return self

    def __exit__(self, *exc_info):
        if self.stream:
            self.stream.stop_stream()
            self.stream.close()
            self.stream = None

    def listen(self, duration):
        for i in range(self.period * duration):
            yield self.stream.read(self.frames_per_buffer)

    def listen_and_score(self, duration, score_fn):
        for frame in self.listen(duration):
            yield frame, score_fn(frame)

    def get_background_rms(self, duration=1):
        """ Get the background volume """
        stack = collections.deque([], maxlen=20)
        for frame, score in self.listen_and_score(duration, lambda x: audioop.rms(x, 2) / 3):
            stack.append(score)
        return sum(stack) / len(stack)

    def passive_listen(self, duration=5):
        """ Listen for a sudden change in volume and then record for a second"""
        self.logger.debug("Started passive listen")
        threshold = self.get_background_rms()
        stack = collections.deque([], maxlen=20)
        for frame, score in self.listen_and_score(duration, lambda x: audioop.rms(x, 2) / 3):
            stack.append(frame)
            if score > threshold:
                self.logger.debug("Recorded as volume went over threshold of %r" % threshold)
                return self._frames_to_wav(list(stack) + list(self.listen(1)))
        self.logger.debug("No audio recorded over threshold of %r" % threshold)

    def active_listen(self, duration=15):
        """ Listen for a specified duration or until 1 second of silence """
        self.logger.debug("Started active listen")
        threshold = self.get_background_rms()
        stack = []
        count = 0
        started = False
        for frame, score in self.listen_and_score(duration, lambda x: audioop.rms(x, 2) / 3):
            stack.append(frame)

            # How many iterations of 'quietness' have we had?
            if score <= threshold:
                count += 1
            else:
                started = True
                count = 0

	    # self.period represents about a second of data - as soon as we
	    # reach that we can return a wav
            if started and count >= self.period:
                self.logger.debug("Stopped listening as you finished blabbing")
                break

            # If silent for 3 seconds then bail out
            if not started and count >= self.period * 3:
                self.logger.debug("Bailed after 3 seconds of silence")
                return
        else:
            self.logger.debug("Stopped listening after %r seconds" % duration)

        return self._frames_to_wav(stack)

    def _frames_to_wav(self, frames):
        with tempfile.SpooledTemporaryFile(mode='w+b') as f:
            wav_fp = wave.open(f, 'wb')
            wav_fp.setnchannels(1)
            wav_fp.setsampwidth(pyaudio.get_sample_size(pyaudio.paInt16))
            wav_fp.setframerate(self.rate)
            wav_fp.writeframes(''.join(frames))
            wav_fp.close()
            f.seek(0)

        return f

# Audio Utils for BoneCrushers

import os.path
from io import IOBase, SEEK_SET

import numpy as np
import pyaudio

from . import wav

def find_soundcard():

    """Look for the 8-channel USB sound card and get its index. Returns -1 if card isn't found."""
    
    p = pyaudio.PyAudio()
    info = p.get_host_api_info_by_index(0)
    numdevices = info.get('deviceCount')

    for i in range(0, numdevices):
        devinfo = p.get_device_info_by_host_api_device_index(0,i)
        if "USB Audio" in devinfo.get("name") and devinfo.get("maxOutputChannels") == 8:
            return i

    # No card found, return -1
    return -1

class AudioStream(IOBase):

    def __init__(self,
                 file=os.path.join(os.path.dirname(__file__),"..","data","8ch_test.wav"),delay_factors=[0,0,0,0,0,0,0,0],
                 mono_source=False):
        
        # test for file existence
        if not os.path.isfile(file):
            raise ValueError(f"Cannot find '{os.path.abspath(file)}'.")
        
        # Open and read file
        try:
            wav_data = wav.get_chunks(os.path.abspath(file))
            wav_data = wav_data[b'data']
        except Exception as e:
            raise ValueError(f"Error reading WAV file: {e}")

        # read 16-bit data
        wav_data_ints = np.frombuffer(wav_data,dtype="int16")

        # determine maximum gap between delay offsets (abs max - abs min)
        delay_max_gap = np.abs(max(delay_factors)) - np.abs(min(delay_factors))
        
        # split data into 8 channels
        if mono_source:
            # if mono source, copy the source to 8 channels
            wav_data_local = [np.copy(wav_data_ints) for _ in range(8)]
        else:
            wav_data_local = [wav_data_ints[x::8] for x in range(8)]

        sample_count = len(wav_data_local[0])

        # shift all delay factors so they are 0-based
        delay_factors = [x - min(delay_factors) for x in delay_factors]

        # how many empty samples to add to the stream
        sample_size = len(wav_data_local[0]) + delay_max_gap

        def internal_get_stream_with_offset(off,n):
            buf = np.zeros(sample_size,dtype="int16")
            buf[off:off+sample_count] = wav_data_local[n]
            return buf
        
        # collect wav channels with applied offsets into class variable
        # this uses the above local function to compute the stream with offset, then
        #   list-comprehends them all together
        # the read function will get **samples** not bytes!
        self.wav_data = [internal_get_stream_with_offset(y,x) for x,y in enumerate(delay_factors)]

        # file-like object values
        self.pos = 0
        self._closed = False

    # Provide len
    def __len__(self):
        return len(self.wav_data[0])

    # Implement IOBase interface
    def close(self):
        self._closed = True
        self.pos = 0
    @property
    def closed(self):
        return self._closed
    def seek(self, pos, whence=SEEK_SET):
        if whence == 0:
            self.pos = pos
        elif whence == 1:
            self.pos += pos
        elif whence == 2:
            self.pos = self.__len__() + pos
        if self.pos < 0:
            self.pos = 0
        if self.pos >= self.__len__():
            self.pos = self.__len__()
    def tell(self):
        return self.pos
    def isatty(self):
        return False
    def readable(self):
        return True
    def writable(self):
        return False
    def seekable(self):
        return True
    def read(self, size = -1):
        if self._closed:
            return bytes([]) # file closed, return nothing
        if size == -1:
            read_len = self.__len__() - self.pos
        elif self.pos + size >= self.__len__():
            read_len = self.__len__() - self.pos
        else:
            read_len = size
        buf = np.zeros(read_len * 8,dtype="int16")

        for x in range(8):
            buf[x::8] = self.wav_data[x][self.pos:self.pos+read_len]

        self.pos += read_len
        # WARNING: i'll say it again, this returns SAMPLES/FRAMES, not bytes!!!
        return buf.tobytes()

import numpy as np
import pyaudio
from rich.progress import Progress, TextColumn, MofNCompleteColumn, BarColumn, FileSizeColumn, TimeRemainingColumn

from bonecrushers.library import audio
from bonecrushers.library import wav

import time

class player():

    pos = 0
    abort = False

    pbar = None
    task = None

    right_delay = 0
    
    def callback(self, in_data, frame_count, time_info, status):
        # 8 channel
        
        these_samples_list = [self.wav_data[x][self.pos:self.pos+frame_count] for x in range(8)]

        these_samples = np.zeros((these_samples_list[0].size * 8,), dtype=these_samples_list[0].dtype)
        for x in range(len(self.wav_data)):
            these_samples[x::8] = these_samples_list[x]

        self.pos += frame_count
        
        these_samples_bytes = these_samples.tobytes()        
        self.pbar.update(self.task,advance=frame_count)
       
        return (these_samples_bytes, pyaudio.paContinue)

    def callback2(self, in_data, frame_count, time_info, status):
        
        if self.abort:
            return (bytes(), pyaudio.paAbort)
    
        # get samples
        these_samples_left = self.wav_data[0][self.pos:self.pos+frame_count]

        #second = int(self.pos / 4410) % 8
        second = 0
        # combine the two samples into one longer array
        # source: https://stackoverflow.com/questions/5347065/interleaving-two-numpy-arrays-efficiently
        these_samples = np.zeros((these_samples_left.size * 8,), dtype=these_samples_left.dtype)
        these_samples[second::8] = these_samples_left
        self.pos += frame_count

        these_samples_bytes = these_samples.tobytes()        
        self.pbar.update(self.task,advance=frame_count)

        #print(these_samples)
        # If len(data) is less than requested frame_count, PyAudio automatically
        # assumes the stream is finished, and the stream stops.
        
        return (these_samples_bytes, pyaudio.paContinue)

    # Define callback for playback (1)
    def callback_orig(self, in_data, frame_count, time_info, status):
        
        if self.abort:
            return (bytes(), pyaudio.paAbort)
    
        # get samples
        these_samples_left = self.wav_data[0][self.pos:self.pos+frame_count]

        if self.pos - self.right_delay < 0:
            these_samples_right = np.zeros(these_samples_left.size,dtype="int16")
            if self.pos + frame_count - self.right_delay > 0:
                these_samples_right[self.right_delay:] = self.wav_data[0][self.pos:self.pos+frame_count-self.right_delay]
        else:
            these_samples_right = self.wav_data[0][self.pos-self.right_delay:self.pos+frame_count-self.right_delay]
        self.pos += frame_count

        #this_sample_left += bytes([0,0,0,0,0,0,0,0,0,0,0,0,0,0])
        #this_sample_left += bytes([0,0])

        # combine the two samples into one longer array
        # source: https://stackoverflow.com/questions/5347065/interleaving-two-numpy-arrays-efficiently
        these_samples = np.empty((these_samples_left.size + these_samples_right.size,), dtype=these_samples_left.dtype)
        these_samples[0::2] = these_samples_left
        these_samples[1::2] = these_samples_right

        these_samples_bytes = these_samples.tobytes()        
        self.pbar.update(self.task,advance=frame_count)

        #print(these_samples)
        # If len(data) is less than requested frame_count, PyAudio automatically
        # assumes the stream is finished, and the stream stops.
        
        return (these_samples_bytes, pyaudio.paContinue)

    def play(self):
                
        sid = audio.find_soundcard()
        print(f"soundcard ID: {sid}")

        if sid == -1:
            print("can't find soundcard.")
            exit(1)
        print("read audio...")
        wav_data = wav.get_chunks("/home/fmillion/src/bonecrushers-sw/bonecrushers/data/8ch_test.wav")
        wav_data = wav_data[b'data']

        # split data into two channels of ints
        print("convert audio to ints...")
        wav_data_ints = np.frombuffer(wav_data,dtype="int16")

        print("get channels.")
        self.wav_data = [wav_data_ints[x::8] for x in range(8)]

        print(self.wav_data)
        print(f"length of audio: {len(wav_data)} bytes, {len(self.wav_data[0])} samples")

        print("starting the playback.")

        # Instantiate PyAudio and initialize PortAudio system resources (2)
        p = pyaudio.PyAudio()

        self.abort = False

        # Open stream using callback (3)
        stream = p.open(format=p.get_format_from_width(2),
                        channels=8,
                        rate=44100,
                        output=True,
                        output_device_index=sid,
                        stream_callback=self.callback)

        self.pbar = Progress(
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            MofNCompleteColumn(),
            TimeRemainingColumn(),
        )

        self.task = self.pbar.add_task("[green]Playback", total=len(self.wav_data[0]))
        self.pbar.start()
        self.pbar.start_task(self.task)

        # Wait for stream to finish (4)
        while stream.is_active():
            try:
                time.sleep(0.1)
            except KeyboardInterrupt:
                self.abort=True

        self.pbar.stop()

        # Close the st[ream (5)
        stream.close()

        # Release PortAudio system resources (6)
        p.terminate()

player().play()

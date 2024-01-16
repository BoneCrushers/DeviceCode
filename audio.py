import numpy as np
import pyaudio
from rich.progress import Progress, TextColumn, MofNCompleteColumn, BarColumn, FileSizeColumn, TimeRemainingColumn

from bonecrushers.library import audio

import time

class player():

    abort = False

    pbar = None
    task = None

    def callback(self, in_data, frame_count, time_info, status):        
        self.pbar.update(self.task,advance=frame_count)
        return (self.sound_obj.read(frame_count), pyaudio.paContinue)

    def play(self):
        
        sid = audio.find_soundcard()
        print(f"soundcard ID: {sid}")

        if sid == -1:
            print("can't find soundcard.")
            exit(1)
        print("read audio...")
        self.sound_obj = audio.AudioStream(
            file="bonecrushers/data/music.wav",
            delay_factors=[0,48,0,96,0,441,0,882],
            mono_source=True)
        
        print(f"length of audio: {len(self.sound_obj)*8} bytes, {len(self.sound_obj)} samples")

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

        self.task = self.pbar.add_task("[green]Playback", total=len(self.sound_obj))
        self.pbar.start()
        self.pbar.start_task(self.task)

        # Wait for stream to finish (4)
        while stream.is_active():
            try:
                time.sleep(0.1)
            except KeyboardInterrupt:
                self.sound_obj.close()

        self.pbar.stop()

        # Close the st[ream (5)
        stream.close()

        # Release PortAudio system resources (6)
        p.terminate()

if __name__ == "__main__":
    player().play()
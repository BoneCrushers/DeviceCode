import tkinter as tk
from tkinter import ttk
import GUI
import time
import numpy as np
import Ambisonics
import os
from tkinter.filedialog import askopenfilename





class AmbisonicsGUI:
    def __init__(self, speakerData, width=500, height=500):

        self.window = tk.Tk()
        self.window.title("Ambisonics Editor")
        self.window.geometry("500x500")
        tk.ttk.Button(self.window, text="Play", command=self.playSound).grid(row=5, column=1, padx=0, pady=0)
        tk.ttk.Button(self.window, text="Select a file", command=self.selectFile).grid(row=5, column=0, padx=0, pady=0)

        joystickSliderFrame = tk.Frame()
        joystickSliderFrame.grid(row=2, column=0, columnspan=1, pady=10)

        volumeSliderFrame = tk.Frame()
        volumeSliderFrame.grid(row=2, column=1, columnspan=1, pady=10)

        checkboxesFrame = tk.Frame()
        checkboxesFrame.grid(row=4, column=0, columnspan=2, pady=10, padx=10)

        transducersLabel = tk.Label(text='Select Transducers', font=("Arial", 15))
        transducersLabel.grid(row=3, column=0, padx=90, columnspan=2, pady=10)
        self.circleWithCoordinates = GUI.JoyStick(joystickSliderFrame, self)
        self.slider = GUI.Slider(joystickSliderFrame, self)
        self.volumeSlider = GUI.VolumeSlider(volumeSliderFrame, self)
        self.checkboxes = GUI.Checkboxes(checkboxesFrame, self)

        self.angleData = 0
        self.audioInProgress = False
        self.speakerData = speakerData
        self.AmbisonicsObj = Ambisonics.PlayAmbisonics(window=self, speakerData=speakerData,
                                                       fileName= os.getcwd()+"\\SoundFiles\\CenterMONO.wav")

        self.queueList = []

        # TEST
        self.Permaplay = True

    def getCoords(self):
        """
        :return: (x value, y value, z value) - extracted data from the GUI Panel
        """
        t = self.circleWithCoordinates.getData()
        coords = (t[0], t[1], int(self.slider.getData()))
        return coords

    def loop(self):
        """
        main loop for Window, should not end.
        """
        try:
            while True:
                for L in range(len(self.queueList)):
                    i = self.queueList.pop(0)
                    assert (i.__class__ == QueueObject)
                    i.update()

                temp = self.getAngleData()
                if temp != self.angleData:
                    self.angleData = temp

                    # TEST
                    print(round(temp[0], 3), round(temp[1], 3), round(temp[2], 3))

                    self.AmbisonicsObj.updateSoundLocationData()
                # # TEST
                # if self.Permaplay and not self.audioInProgress:
                #     self.playSound()

                self.window.update_idletasks()
                self.window.update()
                time.sleep(.01667)  # sleep time for 60 fps
        except Ambisonics.AmbEndOfFileError:
            print("Exception condition met, exiting loop")

    def playSound(self):
        """
        Plays the sound if not playing, pauses if playing
        """
        if self.audioInProgress:
            print("playsound ending audio")
            self.AmbisonicsObj.stopAudioChannel()
            tk.ttk.Button(self.window, text="Play", command=self.playSound).grid(row=5, column=1,
                                                                                 padx=0, pady=0)
        else:
            print("playsound starting audio")
            self.AmbisonicsObj.startAudioChannel()
            tk.ttk.Button(self.window, text="Pause", command=self.playSound).grid(row=5, column=1,
                                                                                  padx=0, pady=0)
        self.audioInProgress = not self.audioInProgress

    def getAngleData(self):
        """
        :return: (theta, zenith, distance) angles measured in radians, 0 <= dist <= 1
        """
        data = self.getCoords()
        if (data[0], data[1]) == (0, 0):
            theta = 0.0
        else:
            theta = (-1 * np.arctan2(data[1], data[0]) - np.pi / 2) % (2 * np.pi)
        if (data[1], data[2]) == (0, 0):
            zenith = 0.0
        else:
            zenith = (-1 * np.arctan2(data[2], data[1]) + np.pi) % (2 * np.pi)
        dist = (np.sqrt(np.power(data[0], 2) + np.power(data[1], 2) + np.power(data[2], 2))) / 75

        # TEST SQUARE DIST
        return theta, zenith, np.float_power(dist, 1.5)
    
    def selectFile(self):
        if(self.audioInProgress):
            self.playSound()
        
        fileexplorer = tk.Tk()
        fileexplorer.withdraw()
        filename = askopenfilename(initialdir= os.getcwd()+"\\SoundFiles\\")

        self.AmbisonicsObj = Ambisonics.PlayAmbisonics(window=self, speakerData=self.speakerData,
                                                       fileName=filename)

    def setSpeakerInformation(self, speakerData):
        self.speakerData = speakerData
        self.AmbisonicsObj.updateSpeakerInformation(speakerData)
        self.AmbisonicsObj.updateSpeakerList()





class QueueObject:
    def __init__(self, obj, func):
        self.obj = obj
        self.func = func

    def update(self):
        self.func(self=self.obj)

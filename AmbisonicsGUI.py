import tkinter as tk
from tkinter import ttk
import GUI
import time
import numpy as np
import Ambisonics


    
class AmbisonicsGUI:
    def __init__(self):
        self.window = tk.Tk()
        self.window.geometry("500x500")
        playButton = tk.ttk.Button(self.window, text= "Play", command=self.playSound).grid(row=5, column=1, padx=0, pady=0)
        
        joystickSliderFrame = tk.Frame()
        joystickSliderFrame.grid(row=2, column=0, columnspan=2, pady=10)

        checkboxesFrame = tk.Frame()
        checkboxesFrame.grid(row=4, column=0, columnspan=2, pady=10, padx=10)

        titleLabel = tk.Label(text='Ambisonics Editor', font=("Arial", 20))
        titleLabel.grid(row=0, column=0, pady=10, padx=90, columnspan=2)
        transducersLabel = tk.Label(text='Select Transducers', font=("Arial", 15))
        transducersLabel.grid(row=3, column=0, padx=90, columnspan=2, pady=10)
        self.circleWithCoordinates = GUI.JoyStick(joystickSliderFrame)
        self.slider = GUI.Slider(joystickSliderFrame, self)
        self.checkboxes = GUI.Checkboxes(checkboxesFrame)

        self.angleData = 0
        self.audioInProgress = False
        self.AmbisonicsObj = Ambisonics.PlayAmbisonics(window=self, speakerData=[[90, 0, 1, 0], [270, 0, 1, 1]], fileName="CenterMONO.wav")
    
    def getCoords(self):
        """
        (x value, y value, z value) - extracted data from the GUI Panel
        """
        t = self.circleWithCoordinates.getData()
        coords = (t[0], t[1], self.slider.getData())
        return coords
    
    def loop(self, callAgain:bool =True):
        while callAgain:
            try:
                while True:
                    self.window.update_idletasks()
                    self.window.update()
                    temp = self.getAngleData()
                    if(temp != self.angleData):
                        self.angleData = temp
                        print(round(temp[0], 3), round(temp[1], 3), round(temp[2], 3))
                        self.AmbisonicsObj.updateSoundLocationData()
                    time.sleep(.01667) #sleep time for 60 fps
            except Ambisonics.AmbEndOfFileError:
                print("Exception condition met, exiting loop")
                

    def playSound(self):
        """
        get file name (**make selectable**)
        get volume
        """
        if(self.audioInProgress):
            print("playsound ending audio")
            self.AmbisonicsObj.stopAudioChannel()
        else:
            print("playsound starting audio")
            self.AmbisonicsObj.startAudioChannel()
        self.audioInProgress = not self.audioInProgress

    def getAngleData(self):
        """
        get file name (**make selectable**)
        get speaker data, need X, Y, Z, convert XYZ to theta/zenith/ *DIST*
        """
        data = self.getCoords()
        if((data[0], data[1]) == (0, 0)):
            theta = 0.0
        else:
            theta = (-1*np.arctan2(data[1], data[0]) - np.pi/2) % (2*np.pi)
        if((data[1], data[2]) == (0, 0)):
            zenith = 0.0
        else:
            zenith = (-1*np.arctan2(data[2], data[1]) + np.pi) % (2*np.pi)
        dist = (np.sqrt(np.power(data[0], 2) + np.power(data[1], 2) + np.power(data[2])))/75

        return (theta, zenith, dist)
    
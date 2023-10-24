import tkinter as tk
from tkinter import ttk
import GUI
import Ambisonics

def playSound():
    """
    get file name (**make selectable**)
    get speaker data
    get volume
    """
    Ambisonics.PlayAmbisonics("Center.wav", speakerData=[[270, 0, 1, 0], [90, 0, 1, 1]], ambvolume=.5)

if __name__ == '__main__':
    window = tk.Tk()
    window.geometry("600x600")

    playButton = tk.ttk.Button(window, text= "Play", command=playSound).grid(row=5, column=1, padx=0, pady=0)
    
    joystickSliderFrame = tk.Frame()
    joystickSliderFrame.grid(row=2, column=0, columnspan=2, pady=10)

    checkboxesFrame = tk.Frame()
    checkboxesFrame.grid(row=4, column=0, columnspan=2, pady=10, padx=10)

    titleLabel = tk.Label(text='Ambisonics Editor', font=("Arial", 20))
    titleLabel.grid(row=0, column=0, pady=10, padx=90, columnspan=2)
    transducersLabel = tk.Label(text='Select Transducers', font=("Arial", 15))
    transducersLabel.grid(row=3, column=0, padx=90, columnspan=2, pady=10)
    circleWithCoordinates = GUI.JoyStick(joystickSliderFrame)
    slider = GUI.Slider(joystickSliderFrame)
    checkboxes = GUI.Checkboxes(checkboxesFrame)


    

    window.mainloop()



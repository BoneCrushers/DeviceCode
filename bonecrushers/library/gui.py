import tkinter as tk
import numpy as np

class JoyStick:
    def __init__(self, parent, window):
        """
        Joystick for the X and Y values when placing the mono audio in 3D space.
        :parent: tk.Frame object
        :window: AmbisonicsGUI object holding this object
        """
        self.frame = tk.Frame(parent, height=200, width=150)
        self.width, self.height = 200, 200  # for canvas circles will be drawn on
        self.canvas = tk.Canvas(self.frame, width=self.width, height=self.height)
        self.center = (self.width / 2, self.height / 2)
        self.canvas.bind("<Button-1>", self.onMouseClickDrag)
        self.canvas.bind("<B1-Motion>", self.onMouseClickDrag)
        self.outerRadius = 74
        self.innerCircle = None
        self.innerCircleRadius = 10
        self.innerCircleCoords = (0, 0)  # Initialize the inner circle at (0, 0)
        self.coordinatesLabel = tk.Label(self.frame, text=f'(x,y): ({0},{0})')
        self.drawOuterCircle(self.outerRadius)
        self.drawInnerCircle()
        self.drawOuterCircle(2)
        self.coordinatesLabel.pack(side='bottom')
        self.frame.grid(row=1, column=0, padx=10, pady=10)  # grid for joystick frame
        self.canvas.pack()
        self.window = window

    def drawOuterCircle(self, outerRadius):
        self.canvas.create_oval(
            self.center[0] - outerRadius,
            self.center[1] - outerRadius,
            self.center[0] + outerRadius,
            self.center[1] + outerRadius,
            outline="black",
            width=3
        )

    def drawInnerCircle(self):
        if self.innerCircle:
            self.canvas.delete(self.innerCircle)
        x, y = self.innerCircleCoords
        self.innerCircle = self.canvas.create_oval(
            self.center[0] + x - self.innerCircleRadius,
            self.center[1] + y - self.innerCircleRadius,
            self.center[0] + x + self.innerCircleRadius,
            self.center[1] + y + self.innerCircleRadius,
            outline="black",
            fill="black",
        )

    def onMouseClickDrag(self, event, data=None):
        """
        Bound to mouse click or drag, deals with the change of x and y coordinates
        :event: event causing the call, ignored if data is not None
        :data: Tuple, (X, Y), used when manually setting values, event is ignored if used.
        :return: none
        """
        if(data is not None):
            x, y = int(data[0]), int(data[1])
        else:
            x, y = int(event.x - self.center[0]), int(event.y - self.center[1])

        distance = np.sqrt(np.power(x, 2) + np.power(y, 2))

        # Ensure the click or drag is inside or on the outer circle
        if distance <= self.outerRadius:
            self.innerCircleCoords = (x, y)
        else:
            # Calculate the point on the outer circle closest to the click
            ratio = self.outerRadius / distance
            x = int(x * ratio)
            y = int(y * ratio)
            self.innerCircleCoords = (x, y)

        self.drawInnerCircle()
        self.coordinatesLabel.config(
            # y coordinate displays opposite so reversing the sign
            text=f'(x,y): ({self.innerCircleCoords[0]},{-1 * self.innerCircleCoords[1]})')

        self.evaluate3D(self.window.slider, (x, y, self.window.slider.getData()))

    def getData(self):
        return self.innerCircleCoords
    
    def setData(self, data):
        """
        sets coordinates of the joystick to the values provided.
        :data: Tuple (X, Y)
        """
        self.onMouseClickDrag(event=None, data=(data[0], -data[1]))

    def evaluate3D(self, slider, data=(0, 0, 0)):
        """
        :slider: the slider object to adjust if the point generated is outside of a sphere, uses the Z value from the slider in the calculations. 
        :return: None
        """
        slider.onSliderChange(None)


class Slider:
    def __init__(self, parent, window):
        """
        Creates a slider that can be used to adjust a Z value of an AmbisonicsGUI Object
        :parent: tk.Frame object
        :window: AmbisonicsGUI object holding this object
        """
        self.frame = tk.Frame(parent, height=175, width=175, padx=10)
        self.sliderValue = 0
        self.slider = tk.Scale(self.frame, from_=74, to=-74, orient='vertical', length=150, showvalue=False,
                               command=self.onSliderChange)
        self.label = tk.Label(self.frame, text=f"z: {0}")
        self.slider.pack(pady=10)
        self.label.pack(pady=10)
        self.frame.grid(row=1, column=1, padx=20, pady=10)  # Place in the grid

        self.window = window

    def onSliderChange(self, event):
        temp = self.window.circleWithCoordinates.getData()
        value = self.evaluate3D(self.slider, (temp[0], temp[1], self.slider.get()))
        self.label.config(text=f"z: {value}")

    def getData(self):
        return self.slider.get()

    def setData(self, value):
        self.slider.set(value)
        self.onSliderChange(None)

    def evaluate3D(self, slider, data=(0, 0, 0)):
        """
        Checks if the new value is inside of a circle with a radius of 75, forces the point inside by changing Z (slider) value if not
        :slider: Scale to be checked
        :return: integer, value after necessary adjustments have been made"""
        dist = np.sqrt(np.power(data[0], 2) + np.power(data[1], 2) + np.power(data[2], 2))
        if dist >= 75:
            val = int(abs(np.sqrt(5476 - np.power(data[0], 2) - np.power(data[1], 2))))
            if self.slider.get() < 0:
                val = -val
            slider.set(val)
            #TEST
            print("Value outside of sphere, adjusting automatically.")
        return slider.get()

class VolumeSlider:
    def __init__(self, parent, window):
        """
        Creates a slider that can be used to adjust the volume of an AmbisonicsGUI Object
        :parent: tk.Frame object
        :window: AmbisonicsGUI object holding this object
        """
        self.frame = tk.Frame(parent, height=175, width=175, padx=10)
        self.volume = 25
        
        self.label = tk.Label(self.frame, text=f"Volume: {self.volume}")
        self.slider = tk.Scale(self.frame, from_=100, to=0, orient='vertical', length=150, showvalue=False,
                               command=self.onChange)
        self.slider.pack(pady=10)
        self.label.pack(pady=10)
        self.frame.grid(row=1, column=1, padx=20, pady=10)  # Place in the grid

        self.window = window

        
    def onChange(self, event):
        self.volume = self.slider.get()
        self.label.config(text=f"Volume: {self.volume}")
        self.window.AmbisonicsObj.setVolume(self.volume/100)
    
    def getVolume(self):
        return self.volume
    
    def setVolume(self, vol):
        self.volume = vol
        

class Checkboxes:
    def __init__(self, parent, window, numboxes=8):
        """
        Creates selections for an AmbisonicsGUI object that can change the selected transducers
        :parent: tk.Frame object
        :window: AmbisonicsGUI object holding this object
        :numboxes: number of transducers, default 8, recommended not to change
        """
        self.checkboxStatus = [True] * numboxes  # Initialize the checkbox statuses
        self.checkboxes = self.createCheckboxes(parent, numboxes)
        self.window = window

    def createCheckboxes(self, parent, numboxes):
        createdCheckboxes = []
        for i in range(numboxes):
            checkboxVar = tk.BooleanVar(value=True)
            checkbox = tk.Checkbutton(parent, text=f'{i + 1}',
                                      command=lambda x=i, var=checkboxVar: self.onClick(x), variable=checkboxVar)
            checkbox.grid(row=0, column=i, padx=5)
            createdCheckboxes.append(checkbox)
        return createdCheckboxes

    def onClick(self, checkbox_index):
        self.checkboxStatus[checkbox_index] = not self.checkboxStatus[checkbox_index]
        print(self.checkboxStatus)
        temp = self.window.speakerData
        for i in temp:
            if(self.checkboxStatus[i[4]]):
                i[3] = 1
            else:
                i[3] = 0
        self.window.setSpeakerInformation(temp)
        # print(temp)
        

    def getData(self):
        return self.checkboxes

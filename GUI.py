import tkinter as tk


class MovableCircle:
    def __init__(self, parent):
        self.frame = tk.Frame(parent, height=200, width=150)
        self.width, self.height = 200, 200  # for canvas circles will be drawn on
        self.canvas = tk.Canvas(self.frame, width=self.width, height=self.height)
        self.center = (self.width / 2, self.height / 2)
        self.canvas.bind("<Button-1>", self.onMouseClickDrag)
        self.canvas.bind("<B1-Motion>", self.onMouseClickDrag)
        self.outerRadius = 75
        self.innerCircle = None
        self.innerCircleRadius = 12
        self.innerCircleCoords = (0, 0)  # Initialize the inner circle at (0, 0)
        self.coordinatesLabel = tk.Label(self.frame, text=f'(x,y): ({0},{0})')
        self.drawOuterCircle()
        self.drawInnerCircle()
        self.coordinatesLabel.pack(side='bottom')
        self.canvas.pack()
        self.frame.grid(row=1, column=0, padx=10, pady=10)  # grid for joystick frame

    def drawOuterCircle(self):
        self.canvas.create_oval(
            self.center[0] - self.outerRadius,
            self.center[1] - self.outerRadius,
            self.center[0] + self.outerRadius,
            self.center[1] + self.outerRadius,
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

    def onMouseClickDrag(self, event):
        x, y = int(event.x - self.center[0]), int(event.y - self.center[1])
        distance = int((x ** 2 + y ** 2) ** 0.5)

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


class Slider:
    def __init__(self, parent):
        self.frame = tk.Frame(parent, height=175, width=175, padx=10)
        self.sliderValue = 0
        self.slider = tk.Scale(self.frame, from_=75, to=-75, orient='vertical', length=150, showvalue=False,
                               command=self.onSliderChange)
        self.label = tk.Label(self.frame, text=f"z: {0}")
        self.slider.pack(pady=10)
        self.label.pack(pady=10)
        self.frame.grid(row=1, column=1, padx=20, pady=10)  # Place in the grid

    def onSliderChange(self, event):
        value = self.slider.get()
        print(value)
        self.label.config(text=f"z: {value}")


class Checkboxes:
    def __init__(self, parent):
        self.checkboxStatus = [True] * 8  # Initialize the checkbox statuses
        self.checkboxes = self.createCheckboxes(parent)

    def createCheckboxes(self, parent):
        createdCheckboxes = []
        for i in range(8):
            checkboxVar = tk.BooleanVar(value=True)
            checkbox = tk.Checkbutton(parent, text=f'{i + 1}',
                                      command=lambda x=i, var=checkboxVar: self.onClick(x), variable=checkboxVar)
            checkbox.grid(row=0, column=i, padx=5)
            createdCheckboxes.append(checkbox)
        return createdCheckboxes

    def onClick(self, checkbox_index):
        self.checkboxStatus[checkbox_index] = not self.checkboxStatus[checkbox_index]
        print(self.checkboxStatus)


if __name__ == '__main__':
    window = tk.Tk()
    window.geometry("400x400")

    joystickSliderFrame = tk.Frame()
    joystickSliderFrame.grid(row=2, column=0, columnspan=2, pady=10)

    checkboxesFrame = tk.Frame()
    checkboxesFrame.grid(row=4, column=0, columnspan=2, pady=10, padx=10)

    titleLabel = tk.Label(text='Ambisonics Editor', font=("Arial", 20))
    titleLabel.grid(row=0, column=0, pady=10, padx=90, columnspan=2)
    transducersLabel = tk.Label(text='Select Transducers', font=("Arial", 15))
    transducersLabel.grid(row=3, column=0, padx=90, columnspan=2, pady=10)
    circleWithCoordinates = MovableCircle(joystickSliderFrame)
    slider = Slider(joystickSliderFrame)
    checkboxes = Checkboxes(checkboxesFrame)

    window.mainloop()

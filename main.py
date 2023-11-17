import AmbisonicsGUI
import numpy as np

# Run the program:
w = AmbisonicsGUI.AmbisonicsGUI([[-np.pi/2, np.pi/2, 1, 1, 0], #right top, 0
                                 [-np.pi/2, np.pi*3/2, 1, 1, 1], #right bottom, 1
                                 [-np.pi*3/4, np.pi, 1, 1, 2], #right back, 2
                                 [-np.pi/4, 0, 1, 1, 3], #right front, 3
                                 [np.pi/4, 0, 1, 1, 4], #left front, 4
                                 [np.pi/2, np.pi/2, 1, 1, 5], #left top, 5
                                 [np.pi/2, np.pi*3/2, 1, 1, 6], #left bottom, 6
                                 [np.pi*3/4, np.pi, 1, 1, 7]] #left back, 7
                                )
w.loop()

"""
[
[np.pi/4, 0, 1, 1, 4], #left front, 4
[-np.pi/4, 0, 1, 1, 3], #right front, 3
[np.pi*3/4, np.pi, 1, 1, 7], #left back, 7
[-np.pi*3/4, np.pi, 1, 1, 2], #right back, 2
[np.pi/2, np.pi/2, 1, 1, 5], #left top, 5
[-np.pi/2, np.pi/2, 1, 1, 0], #right top, 0
[np.pi/2, np.pi*3/2, 1, 1, 6], #left bottom, 6
[-np.pi/2, np.pi*3/2, 1, 1, 1] #right bottom, 1
]

port 0/1:
top, bottom          right ear
port 2/3:
front back           right ear
port 4/5:
top front            left ear
port 6/7:
bottom back          left ear


"""
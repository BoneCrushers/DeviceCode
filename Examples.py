import numpy as np


data = np.arange(start=0, stop=256, dtype=np.int16)

AD = np.ndarray((64, 4), dtype=data.dtype, buffer=data)
ADT = AD.T

print("Data as bytes")
print(bytes(data))
print("\nStarting with just an example of the data we may read in. This is a 72 item, 1 dimensional (1D), numpy array\nData Array")
print(data)
print("\nHere, we turn that 1D array into 2D, effectively our frames of data\n2D-Data array")
print(AD)
print("\nFinally, this is what we use. We transpose the 2D array, flipping it using its corner (0,0) as an axis\nNow we have 4 arrays which in our sound file would be the 4 channels (W,X,Y,Z), in whatever order they appear\nNote: this is a view, {}, not a copy which means all we have to do\nwhen returning the data is return the byte data of the 2D array which will flatten when converted\nTransposed 2D-Data Array".format(ADT.__class__))
print(ADT)

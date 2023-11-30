# DeviceCode
To run the program, you will need to download a couple packages if they are not already installed. These include: numpy, tkinter, and pyaudio, while some that likely come with installation of python are os, time, and struct
to download each of these packages, go into the python console and type:
pip install ""name""
where ""name"" is the name of the package you are installing, ie. numpy or tkinter

In order to play sound, simply create an AmbisonicsGUI object and run its loop function. Doing this will open a window with a bunch of dials and siders but also with a play button in the bottom right. Clicking that one time will run the currently selected file, and clicking it while a file is running will stop that playback.

Internally, audio playback is done through creating an Ambisonics object. This object does most of the work for you, it will open and read the header, locate the start of the data, and on calling the startAudioChannel() call, will start playback. it is recommended to do this through the GUI, as many pieces of data the calculations used are tied to it.

The audio will play onto 8 channels, specified when initializing the ambisonics object and changable through a set of functions. Each speaker has its own set of data in this format: [Theta angle(radians), Zenith angle(radians), SpeakerConstant, on/off, Data Line (0-7)]. In the case that only a small number of these channels are used, leave the empty channels as 0 item lists. To specify an order, edit the fifth item in the speaker's data set to change the channel it goes on (0-7). Repeats are not allowed, and order is recommended to prevent headaches but not required. Theta and Zenith are angles relative to facing directly forward, where a positive change in Theta is a rotation left and a positive change in Zenith is a rotation up. Speaker constant is an additional variable usable to individually adjust the output of each speaker. This is multiplied directly with the data set during calculations, but be warned: overloading this number can cause excessive clipping, try to keep it below 2 and understand that clipping is more likely the higher you go. On/off is a variable tied to the transducer selection and is effectively a multiplier, where 0 turns the transducer off and 1 is on. This number is edited any time a transducer is selected, so note any changes you make to this will only last until a transducer has been changed.

The speakers themselves are adjusted through the speakerdata list in the AmbisonicsGUI parameters. That list follows the same rule set for angles as the sound location data, where facing forward is (0, 0), (theta, zenith). It also has 3 other parameters: the speaker constant, which is an adjustable multiplier used in calculations to affect the output; on/off which is used by the transducers selection to turn a speaker on (1) or off (0); and channel, which specifies what channel to output the data on. Multiple speakers on one channel is not allowed.





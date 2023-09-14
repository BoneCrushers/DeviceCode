import pyaudio
import wave
import numpy as np
import os

# Initializing wav file
wav_file = os.getcwd()+"\\SoundFiles\\"+      "Harry-Potter-Theme.wav"
wf = wave.open(wav_file, 'rb')


def changeVolume(audioData, volume):
    dataArray = np.frombuffer(audioData, dtype=np.int16)
    newAudio = (dataArray * volume).astype(np.int16)
    return newAudio.tobytes()


# Define callback function to process and adjust audio data
def audioCallback(inData, frameCount, timeInfo, status):
    audioData = wf.readframes(frameCount)
    audioData = changeVolume(audioData, .1)
    print(len(audioData))
    print(audioData)
    return audioData, pyaudio.paContinue

def audioCallbackChannel(inData, frameCount, timeInfo, status):
    audioData = wf.readframes(frameCount)
    audioData = changeVolume(audioData, .1)
    editedAudioData = []
    #Select Channels here, 0-7 with each channel being 2 T/F, enter the channels you wish to select as a tuple of T/F
    #Note: know your input for now, selecting the wrong number of channels will output unintentended data
    #TESTING NOTES:
    #CHANNEL SEPARATION:
        # 7.1 Audio Standard: (Look at again with results below, may map different than believed)
        # 1 = Left
        # 2 = Right
        # 3 = Center
        # 4 = LFE
        # 5 = Side Left
        # 6 = Side Right
        # 7 = Back Left
        # 8 = Back Right

        #Testing: Made significant progress since talking with Flint
        #   1/2: Left side Front plug, Normal Volume; left side Back plug, Normal Volume
        #   3/4: Right side Front plug, Normal Volume; right side Back plug, Normal Volume
        #   5/6: Left side Surround plug, Normal Volume; left side Center plug, Normal Volume
        #   7/8: Right side Front plug, Normal Volume; right side Back plug, Normal Volume


#Portaudio check and see if it does anything on its own
    ChannelSelect = (False, False, False, False, False, False, False, False, False, False, False, False, True, True, True, True)
    #ChannelSelect = (True, True, False, False, False, False, False)
    ad = iter(audioData)
    try:
        # 'i' is a counter for bytes, equal to how large the finalized data array should be.
        # used as a filter to select which channels we want to put our useful data on.
        BYTES_PER_INTEGER = 2
        CHANNEL_COUNT = 8
        FRAME_SIZE_IN_BYTES = BYTES_PER_INTEGER*CHANNEL_COUNT
        for i in range(frameCount*FRAME_SIZE_IN_BYTES):
            # Input data into selected channel, with zeroes in the other  channels
            if(ChannelSelect[i%CHANNEL_COUNT*2]):
                editedAudioData.append(int(next(ad)))
            if(ChannelSelect[i%CHANNEL_COUNT*2] is not True):
                editedAudioData.append(0)
            else:
                editedAudioData.append(0)
                # next(ad)
    except StopIteration:
        pass
    
    returnData = bytes(editedAudioData)
    return returnData, pyaudio.paContinue


def playAudio(file, speed=1):
    # Initialize PyAudio
    p = pyaudio.PyAudio()
    # Open a stream to sound card with the callback function
    stream = p.open(format=p.get_format_from_width(wf.getsampwidth()),
                    channels=wf.getnchannels(),
                    rate=int(wf.getframerate() * speed),
                    output=True,
                    stream_callback=audioCallback)
    # Start the stream
    stream.start_stream()
    while stream.is_active():
        pass
    # Close the stream and PyAudio
    stream.stop_stream()
    stream.close()
    p.terminate()

    # Close the WAV file
    wf.close()

def playAudioChannel(file, speed=1):
    # Initialize PyAudio
    p = pyaudio.PyAudio()
    # Open a stream to sound card with the callback function
    stream = p.open(format=pyaudio.get_format_from_width(wf.getsampwidth()), 
                    channels=8,
                    rate=int(wf.getframerate() * speed),
                    output=True, 
                    stream_callback=audioCallbackChannel)
    # Start the stream
    stream.start_stream()
    while stream.is_active():
        pass
    # Close the stream and PyAudio
    stream.stop_stream()
    stream.close()
    p.terminate()

    # Close the WAV file
    wf.close()


# def audioTest1():
#     #Test Data Collection
#     testvals = []
#     #Testing for numbers
#     framesToRead = 6000
#     testvals.append("framesToRead: " + str(framesToRead))
#     framesRawData = wf.readframes(framesToRead)

#     testvals.append("len(framesRawData): " + str(len(framesRawData)))
#     channels = wf.getnchannels() #array size, one - 2 byte integer for each lane in an array
#     testvals.append("channels: " + str(channels))
#     intlist = []
#     intlistlist = []
#     #Retrieves range based on input, uses that to iterate through 2 bytes at a time (one integer)
#     for i in range(int(len(framesRawData)/2)):
#         intlist.append(int.from_bytes(framesRawData[(i*2):((i+1)*2)], byteorder='big', signed=True))
#         if(i%channels+1 == channels):
#             intlistlist.append(intlist.copy())
#             intlist = []
    
#     for i in intlistlist:
#         print(i)

#     print(framesRawData[5900*4:6000*4
#                         ])
        
#     print("Test Data Collection:\n", testvals)

# audioTest1()
# playAudio(wav_file, 1)
playAudioChannel(wav_file, 1)






#Utilizing github via command prompt:
#git status
#git add .
#git status
#git commit -m ""
#git push



# Common Variables:
# W = Sound sphere as a whole, all directions. Base for manipulating sound
# X = Front minus Back, positive value correlates to sound in Front
# Y = Left minus Right, positive value correlates to sound on Left side
# Z = Up minus Down, positive value correlates to sound Above

# Speaker Specific Variables:
# a = Azimuth angle, horizontal an  gle relative to the user's front facing direction
# b = Zenith angle, vertical angle relative to the users straight line view.
# c = Speaker constant. This is unique, going to be hard coded, likely as a list, and used as a type of
# volume multiplier for each transducer based on requirements found later. (Ex. a transducer placed just behind
# the ear will be on muscle, thus need to be 'louder' in order to transfer sound as effectively as in front of the ear)

# def playAmbisonicsAudio(file, speed=1):
#     # Initialize Input stream
#     p = pyaudio.PyAudio()
#     # Open a stream to sound card with the callback function
#     stream = p.open(format=p.get_format_from_width(wf.getsampwidth()), 
#                     channels=8,
#                     rate=int(wf.getframerate() * speed),
#                     output=True,
#                     stream_callback=ambisonicsAudioCallback)
    




#     def ambisonicsAudioCallback(inData, frameCount, timeInfo, status):
#         outdata = 

    






#   ***Things to check***
#is it better to separate out the 4 channel 
#Will need to edit both the main play sound function and audiocallback function?


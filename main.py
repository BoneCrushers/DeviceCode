import pyaudio
import wave
import numpy as np

# Initializing wav file, Note: for file location, forward slashes must be doubled to prevent commands being called
wav_file = "C:\\Users\\nrsch\\OneDrive\\Desktop\\DeviceCode\\SoundFiles\\RatchetBangingOnMetal.wav"
wf = wave.open(wav_file, 'rb')


def changeVolume(audioData, volume):
    dataArray = np.frombuffer(audioData, dtype=np.int16)
    newAudio = (dataArray * volume).astype(np.int16)
    return newAudio.tobytes()


# Define callback function to process and adjust audio data
def audioCallback(inData, frameCount, timeInfo, status):
    audioData = wf.readframes(frameCount)
    audioData = changeVolume(audioData, 1)
    return audioData, pyaudio.paContinue


def playAudio(file, speed=1):
    # Initialize PyAudio
    p = pyaudio.PyAudio()
    # Open a stream to sound card with the callback function
    stream = p.open(format=p.get_format_from_width(wf.getsampwidth()), channels=wf.getnchannels(),
                    rate=int(wf.getframerate() * speed),
                    output=True, stream_callback=audioCallback)
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


def audioTest1():
    #Test Data Collection
    testvals = []
    #Testing for numbers
    framesToRead = 16
    testvals.append("framesToRead: " + str(framesToRead))
    framesRawData = wf.readframes(framesToRead)
    #Verify length of data retrieved. Should be 16(frames)*4(channels)*2(bytes)*1(integer)=128
    testvals.append("len(framesRawData): " + str(len(framesRawData))) #**************Something is wrong here****************  =196? 
    #this ratio (12 instead of 8) is consistent, am i understanding something wrong?
    channels = wf.getnchannels() #array size, one 2 byte int for each lane in an array
    testvals.append("channels: " + str(channels))
    intlist = []
    intlistlist = []
    #Retrieves range based on input, uses that to iterate through 2 bytes at a time (one integer)
    for i in range(int(len(framesRawData)/2)):
    #Data doesnt look right. Data in arr is stored in a manner that, if the array is interleaved so that the first
    # 4 integers correspond to W,X,Y,Z of frame 1, the next 4 to frame 2 in that same order and so on. However, the
    #data seems to stick around numbers, in particular powers of 2, rather than being scattered with any sort of randomness
    #this may be compression, may be something else. 
    #Other problem, may not be one after all, is that the W is consistently off from the other values.
    #I feel like it should be some form of combination of all channels, but that may be wrong to since it
    #is fundamentally different in how it measures.

        intlist.append(int.from_bytes(framesRawData[(i*2):((i+1)*2)], byteorder='big', signed=True))
        if(i%channels+1 == channels):
            intlistlist.append(intlist.copy())
            intlist = []
    
    for i in intlistlist:
        print(i)
        
    print("Test Data Collection:\n", testvals)



audioTest1()
#Need to check:
#    should the integers be signed or unsigned? (i think unsigned and offset so that 0 is the minimum amplitude)
#    numbers reformatted into packages of 6 become a lot more consistent, is this something that is missing?




#playAudio(wav_file, 1)
#Note: we may be losing audio, I listened via bluetooth so it may be syncing issues but i ran it at 
# .5 speed twice in succession and saw about 1.5 seconds of lost time, only about 18.5 seconds when a 5 sec file at
# 1/2 speed should result in 20 sec.







# Common Variables:
# W = Sound sphere as a whole, all directions. Base for manipulating sound
# X = Front minus Back, positive value correlates to sound in Front
# Y = Left minus Right, positive value correlates to sound on Left side
# Z = Up minus Down, positive value correlates to sound Above

# Speaker Specific Variables:
# a = Azimuth angle, horizontal angle relative to the user's front facing direction
# b = Zenith angle, vertical angle relative to the users straight line view.
# c = Speaker constant. This is unique, going to be hard coded, likely as a list, and used as a type of
# volume multiplier for each transducer based on requirements found later. (Ex. a transducer placed just behind
# the ear will be on muscle, thus need to be 'louder' in order to transfer sound as effectively as in front of the ear)

#

# def ?()
##This line v will need adjustments, change to read from stream instead of from buffer
#   dataArray = np.frombuffer(audioData, dtype=np.int16)

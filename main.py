import pyaudio
import numpy as np
import os
import math
import struct

# Getting File Directory
wav_file = os.getcwd()+"\\SoundFiles\\"+   "Right"    +".wav"

# Speakers. Input speakers as a list of ORIGIN VALUES, as though you were facing 0|0
# (Azimuth angle, Zenith angle, Speaker Constant, Channel number)
# In this code, this length will be assumed to be either 2 or 8. testing with odd numbers or greater 
# than 8 channels will likely cause a lot of problems with deciding where to map channels, etc
# todo? map channels in a different order than list's order? Is this necessary?
# todo? 

#   (Horizontal angle, Vertical angle, Speaker Constant)      
#   ******  v  EDIT ME  v  ******
SPEAKER_INFORMATION = [
    [90, 0, 1],
    [270, 0, 1],
    [0, 0, 1],
    [180, 0, 1],
    [0, 90, 1],
    [0, 270, 1],
    [0, 0, 1],
    [0, 180, 0]
]


# speakerList will contain an editable version of all the starting information.
# Only changes should be to speakerList[0] and [1] during runtime,

#holds for each speaker their used values in ambisonicsCalculations(), aka takes the sin and cos of each angle, etc.
#temp given speaker information as an initialization value (for correct length), updated immediately after definition
speakerList = SPEAKER_INFORMATION.copy()

def playAmbisonics(wav_file, speakerList=speakerList, ambvolume=.1, speed=1):
    """
    ambfile= .wav file for reading
    ambvolume= volume for file to be played at. 0 <= value <= 1
    speed= speed, float value.

    will be reformatted to main eventually
    Runs calculations to play ambisonics from a file.
    Currently, the ambisonics file is assumed to have some properties:
        data values stored as int16, number of channels is 4, byteorder='little'
    """
    #Open the file, read contents into memory as ambFile
    amb = open(wav_file, 'rb')
    # CONSTANTS BASED ON FILE 
    fileHeader = amb.read(16)
    ambFileData= fileHeader+amb.read(int.from_bytes(fileHeader[4:8], byteorder='little', signed=False)-16)
    amb.close()

    #FINISH ******
    # *Very* informal breakdown of the header via struct.unpack using format laid out by https://www.mmsp.ece.mcgill.ca/Documents/AudioFormats/WAVE/WAVE.html
    # the website's information is not accurate past the speaker position mask
    formatString = '4sL4s4sLHHLLHHHL16s4s190s'
    unpackedHeader = struct.unpack(formatString, ambFileData[0:struct.calcsize(formatString)])
    FILE_SIZE = unpackedHeader[1]
    IN_CHANNEL_COUNT = unpackedHeader[6]
    FRAME_SIZE_IN_BYTES = unpackedHeader[9]
    FRAME_RATE = unpackedHeader[7]




    #returns next set of data to work with. ambFileCurPosition is now a list until i find a way around local unbound error.
    ambFileCurPosition = [ambFileData.find(b'data')+4]
    def getNextData(ambFileData, size, movePointer=True):
        if(movePointer): ambFileCurPosition[0] += size
        return np.frombuffer(ambFileData[ambFileCurPosition[0]-size:ambFileCurPosition[0]], dtype=np.int16)
    
    # multiplies np.ndarray by float(volume) 
    def changeVolumeAmbisonics(audioData, volume=ambvolume):
        audioData = audioData*volume
        return
    
    # finds trig values for each angle in list of 3 item lists, puts them into speakerList
    def updateSpeakerList():
        for i in range(len(SPEAKER_INFORMATION)):
            if len(SPEAKER_INFORMATION[i]) == 3:
                speakerList[i] = [math.sin(SPEAKER_INFORMATION[i][0]*math.pi/180), math.cos(SPEAKER_INFORMATION[i][0]*math.pi/180), math.sin(SPEAKER_INFORMATION[i][1]*math.pi/180), math.cos(SPEAKER_INFORMATION[i][1]*math.pi/180), SPEAKER_INFORMATION[i][2]]
            else:
                speakerList[i] = []
                #create error type to throw here?**********


    updateSpeakerList()
    OUTPUT_CHANNEL_COUNT = len(speakerList)


    #will likely want to get rid of all separated variables, in this case returnData = bytearray()
    def audioCallbackAmbisonics(inData, frameCount, timeInfo, status):
        AD = getNextData(ambFileData, frameCount*FRAME_SIZE_IN_BYTES)
        AD = np.ndarray((int(len(AD)/IN_CHANNEL_COUNT), IN_CHANNEL_COUNT), dtype=AD.dtype, buffer=AD)
        audioData = AD.T
        #4(IN_CHANNEL_COUNT) arrays of length (min(framecount, frames read), for the case we are at the end of file)
        #each holding all values of a specific channel
        # AD = changeVolumeAmbisonics(audioData=AD)

        RD = np.zeros((int(len(audioData[0])), len(speakerList)), dtype=np.int16)
        returnData = RD.T #Transposed view of returnData. Steps must be done separately, and 
        # returnData must stay as a view. Faster and allows us to avoid converting 2D arrays of the data
        # while still altering it in a speedy manner. (1D array*constant, etc.)
        
        #calculations
        #AudioData = [Z, X, W, Y]? What is up with this order?
        #SpeakerList[i] = [sin(azimuth), cos(azimuth), sin(zenith), cos(zenith)]
        # sin(A)*y, cos(A)*x, sin(z)*z
        for i in range(len(speakerList)):
            returnData[i] = speakerList[i][4]*(
                audioData[2] + 
                speakerList[i][0]*audioData[3] + 
                speakerList[i][1]*audioData[1] + 
                speakerList[i][2]*audioData[0]   
                )*.5 #TEMP VOLUME CHANGE
        return RD.tobytes(), pyaudio.paContinue
            

    normalizationMultiplier = [np.float64(ambvolume)]
    def audioNormalizationAmbisonics(audioData, volume, maxOccuringValue):
        MAX_POSSIBLE = 35565 #maximum possible value for the inputted data's type
        MAX_ALLOWED_VOLUME = MAX_POSSIBLE*volume
        volumeDifference = maxOccuringValue-MAX_ALLOWED_VOLUME

        

        print(round(number=normalizationMultiplier[0], ndigits= 5))
        return changeVolumeAmbisonics(audioData=audioData, volume= normalizationMultiplier[0])


    def playAudioChannel(speed=1):
        # Initialize PyAudio
        p = pyaudio.PyAudio()
        # Open a stream to sound card with the callback function
        # CHANNELS Untested for values besides 8 and 2
        stream = p.open(format=8, #paInt16 = 8 
                        channels=OUTPUT_CHANNEL_COUNT,
                        rate=int(FRAME_RATE * speed),
                        output=True, 
                        stream_callback=audioCallbackAmbisonics)
        # Start the stream
        print("Start!")
        stream.start_stream()
        try:
            while stream.is_active():
                pass
        except ValueError:
            stream.stop_stream()
            stream.close()
            p.terminate()


        print("Done!")
        # Close the stream and PyAudio
        stream.stop_stream()
        stream.close()
        p.terminate()



    print(speakerList)
    playAudioChannel(speed)
    #end of playAmbisonics()

playAmbisonics(wav_file, ambvolume=.1, speed=1)
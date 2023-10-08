import pyaudio
import numpy as np
import os
import math
import struct

# Getting File Directory
wav_file = os.getcwd()+"\\SoundFiles\\"+      "Chicago_Amb_Elevated_Train_B-Format_44.1_16.wav"

# Speakers. Input speakers as a list of ORIGIN VALUES, as though you were facing 0|0
# (Azimuth angle, Zenith angle, Speaker Constant, Channel number)
# In this code, this length will be assumed to be either 2 or 8. testing with odd numbers or greater 
# than 8 channels will likely cause a lot of problems with deciding where to map channels, etc
# todo? map channels in a different order than list's order? Is this necessary?
# todo? 

#   (Horizontal angle, Vertical angle, Speaker Constant, Channel number)      
#   ******  v  EDIT ME  v  ******
SPEAKER_INFORMATION = [
    [90, 0],
    [270, 0],
    # [],
    # [],
    # [],
    # [],
    # [],
    # []
]

# speakerList will contain an editable version of all the starting information.
# (for use in combination with accelerometer later. If accelerometer returns true angles,
# then we need a secondary copy to compute changes, if it returns changes since last report, will
# just need to update each time we get that set of data and can remove copy) 
# Only changes should be to speakerList[0] and [1] during runtime,
# and 
# (LATER) todo? replace speakerList with accelerometer calculation using stored current angle and base offset?

# NEED INFO: *RADIANS* FOR SIN() AND COS().
speakerList = []
for i in range(len(SPEAKER_INFORMATION)):
    if len(SPEAKER_INFORMATION[i]) != 0:
        speakerList.append([math.sin(SPEAKER_INFORMATION[i][0]*math.pi/180), math.cos(SPEAKER_INFORMATION[i][0]*math.pi/180), math.sin(SPEAKER_INFORMATION[i][1]*math.pi/180), math.cos(SPEAKER_INFORMATION[i][1]*math.pi/180)])
    else:
        speakerList.append([])

def playAmbisonics(ambFile, ambvolume=.1, speed=1):
    """
    ambfile= .wav file for reading
    ambvolume= volume for file to be played at. 0 <= value <= 1
    speed= speed, float value.

    will be reformatted to main eventually
    Runs calculations to play ambisonics from a file.
    Currently, the ambisonics file is assumed to have some properties:
        data values stored as int16, number of channels is 4, byteorder='little'
    """
    #Open the file
    amb = open(ambFile, 'rb')

    # CONSTANTS BASED ON FILE 
    fileHeader = amb.readline() + amb.readline(17)
    FILE_SIZE = int.from_bytes(fileHeader[4:8], byteorder='little')
    DATA_SIZE = int.from_bytes(fileHeader[40:44], byteorder='little')
    TEST_SIZE = fileHeader[4:8] 
    FORMAT_LENGTH = fileHeader[17-21]
    FRAME_SIZE_IN_BYTES = int.from_bytes(fileHeader[32:34], byteorder='little')
    FRAME_RATE = int.from_bytes(fileHeader[24:28], byteorder='little')
    CHANNEL_COUNT = int.from_bytes(fileHeader[22:24], byteorder='little')
    VALID_BITS_PER_SAMPLE = int.from_bytes(fileHeader[36:38], byteorder='little')
    # VALID_BITS_PER_SAMPLE is incorrect? 
    SUBFORMAT_GUID = fileHeader[43:58]
    formatData = fileHeader[:100]
    #TEST
    print("formatData", formatData)
    print("FORMAT_LENGTH", FORMAT_LENGTH)
    print('fileHeader: ',fileHeader)
    print("len(fileHeader)",len(fileHeader))
    print('TypeOfFormat',int.from_bytes(fileHeader[20:22], byteorder='little'))
    print('FILE_SIZE',FILE_SIZE)
    print("DATA_SIZE", DATA_SIZE)
    print("FileSize", int.from_bytes(TEST_SIZE, byteorder='little')) # Should be near 6.42 MB
    print("FrameSizeInBytes", FRAME_SIZE_IN_BYTES)
    print("FrameRate", FRAME_RATE)
    print("ChannelCount", CHANNEL_COUNT)
    print("ValidBits/Sample", VALID_BITS_PER_SAMPLE)
    print("SUBFORMAT_GUID", SUBFORMAT_GUID)

    #FINISH ******
    formatString = '4sL4s4sLHHLLHHH8s'
    unpackedHeader = struct.unpack(formatString, fileHeader[0:struct.calcsize(formatString)])
    print(struct.calcsize(formatString), unpackedHeader)

    
#maybe do calculations as float, then convert to int only at end?
    def changeVolumeAmbisonics(audioData, volume):
        dataArray = np.frombuffer(audioData, dtype=np.int16)
        newAudio = (dataArray * volume).astype(np.int16)
        return newAudio.tobytes()
    


#will likely want to get rid of all separated variables, in this case returnData = bytearray()
    def audioCallbackAmbisonics(inData, frameCount, timeInfo, status):
        audioData = amb.read(frameCount*FRAME_SIZE_IN_BYTES) 
        returnData = bytearray()
        audioData = changeVolumeAmbisonics(audioData, ambvolume)

        #adByteStart is the counter to track where in audioData we currently are
        adByteStart=0

        for i in range(frameCount):
            #WorkingData holds 1 frame of data, stored as 16 bit integers in 4 slots, 
            #each corresponding to a channel WXYZ
            workingData = [int.from_bytes(audioData[adByteStart+x:adByteStart+x+2], byteorder='little', signed=True) for x in range(0,8,2)]

            # Iterates the speaker list. If a speaker is an empty list, we just append two 0 bytes (for balancing channel numbers),
            # else we append our ambisonics algorithm for determining sound output of the speaker based on angles provided.
            for s in speakerList:
                sampleValue = np.int16(ambisonicsCalculations(workingData, s, returnZero=(len(s)==0)))
                returnData.extend(sampleValue)
            adByteStart += 8
        return bytes(returnData[:(np.int32((len(audioData)>>1)*len(speakerList)*2))]), pyaudio.paContinue 
        #return bytes in data from 0 until (size of read data / input channel count * output channel count * 2 bytes per channel) 
        #bytes per channel and input channel count are constant for our purposes, so we combine and change the divide into a bit shift for faster math

    def ambisonicsCalculations(audioData, speakerData, returnZero=False):
        if returnZero:
            return 0
        #audioData = [W, X, Y, Z]
        #speakerData = [sin(azimuth), cos(azimuth), sin(zenith), cos(zenith), ??speaker Constant??]
        #Calculations Here:
        return (
                audioData[0]/1.414213 + #sqrt(2) gain factor
                speakerData[0]*audioData[1] + #sin(azimuth)*X, the length of the vertical component of the position of our speaker
                speakerData[1]*audioData[2] + #cos(azimuth)*Y, the length of the horizontal component of the position of our speaker
                speakerData[2]*audioData[3]   #sin(zenith)
                )
    
    def playAudioChannel(speed=1):
        # Initialize PyAudio
        p = pyaudio.PyAudio()
        # Open a stream to sound card with the callback function
        # CHANNELS Untested for values besides 8 and 2
        stream = p.open(format=8, #paInt16 = 8 #Maybe try using 24 bit int? would have to split up the data into 3 bytes but would alleviate the overflow problem. Ask team/flint
                        channels=len(speakerList),
                        rate=int(FRAME_RATE * speed),
                        output=True, 
                        stream_callback=audioCallbackAmbisonics)
        # Start the stream
        stream.start_stream()
        try:
            while stream.is_active():
                pass
        except ValueError:
            stream.stop_stream()
            stream.close()
            p.terminate()

            pass

        print("Done!")
        # Close the stream and PyAudio
        stream.stop_stream()
        stream.close()
        p.terminate()

        # Close the WAV file
        amb.close()
    playAudioChannel(speed)

playAmbisonics(wav_file, ambvolume=.5, speed=1)
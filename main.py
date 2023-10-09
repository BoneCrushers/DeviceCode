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

#   (Horizontal angle, Vertical angle, Speaker Constant)      
#   ******  v  EDIT ME  v  ******
SPEAKER_INFORMATION = [
    [90, 0, 1],
    [270, 0, 1],
    # [],
    # [],
    # [],
    # [],
    # [],
    # []
]

# speakerList will contain an editable version of all the starting information.
# Only changes should be to speakerList[0] and [1] during runtime,

#holds for each speaker their used values in ambisonicsCalculations(), aka takes the sin and cos of each angle, etc.
#temp given speaker information as an initialization value (for correct length), updated immediately
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
    #TEST
    # print(struct.calcsize(formatString), unpackedHeader, len(ambFileData))
    FRAME_SIZE_IN_BYTES = unpackedHeader[9]
    FRAME_RATE = unpackedHeader[7]

    #returns next set of data to work with. ambFileCurPosition is now a list until i find a way around local unbound error.
    ambFileCurPosition = [ambFileData.find(b'data')+4]
    def getNextData(ambFileData, size, movePointer=True):
        if(movePointer): ambFileCurPosition[0] += size
        return ambFileData[min(ambFileCurPosition[0]-size, unpackedHeader[1]):min(ambFileCurPosition[0], unpackedHeader[1])]
    
    # multiplies bytearray by float 
    def changeVolumeAmbisonics(audioData, volume):
        # return (audioData).astype(np.int16)*volume
        dataArray = np.frombuffer(audioData, dtype=np.int16)
        newAudio = (dataArray * volume).astype(np.int16)
        return newAudio.tobytes()
    
    # finds trig values for each angle in list of 2 item lists, puts them into original list
    def updateSpeakerList():
        for i in range(len(SPEAKER_INFORMATION)):
            if len(SPEAKER_INFORMATION[i]) == 3:
                speakerList[i] = [math.sin(SPEAKER_INFORMATION[i][0]*math.pi/180), math.cos(SPEAKER_INFORMATION[i][0]*math.pi/180), math.sin(SPEAKER_INFORMATION[i][1]*math.pi/180), math.cos(SPEAKER_INFORMATION[i][1]*math.pi/180), SPEAKER_INFORMATION[i][2]]
            else:
                speakerList[i] = []
                #create error type to throw here**********

    #will likely want to get rid of all separated variables, in this case returnData = bytearray()
    def audioCallbackAmbisonics(inData, frameCount, timeInfo, status):
        audioData = getNextData(ambFileData, frameCount*FRAME_SIZE_IN_BYTES)
        returnData = bytearray()
        audioData = changeVolumeAmbisonics(audioData, ambvolume)

        # b = np.frombuffer(audioData, dtype=np.int16)
        # a = np.ndarray((frameCount, 4), dtype=np.int16, buffer=audioData)
        # a = changeVolumeAmbisonics(a, ambvolume)
        # print(a)
        #a = [[1w1,1w2,1x1...1z2],[2w1,2w2,2x1...2z2],...] length of each inner array = 8

        # a = np.split(ary=audioData, indices_or_sections=frameCount,) #change 'a' to audioData once completed
        #adByteStart is the counter to track where in audioData we currently are
        adByteStart=0

        for i in range(frameCount):
            #WorkingData holds 1 frame of data, stored as 16 bit integers in 4 slots, 
            #each corresponding to a channel WXYZ
            workingData = [int.from_bytes(audioData[adByteStart+x:adByteStart+x+2], byteorder='little', signed=True) for x in range(0,8,2)]

            # Iterates the speaker list. If a speaker is an empty list, we just append two 0 bytes (for balancing channel numbers),
            # else we append our ambisonics algorithm for determining sound output of the speaker based on angles provided.
            for s in speakerList:
                sampleValue = ambisonicsCalculations(workingData, s, returnZero=(len(s)==0))
                returnData.extend(np.int16(sampleValue))
            adByteStart += 8
        return bytes(returnData[:(np.int32((len(audioData))*len(speakerList)/2))]), pyaudio.paContinue 
        #return bytes in data from 0 until (size of read data / input channel count * output channel count * 2 bytes per channel) 
        #bytes per channel (2) and input channel count (4) are constant for our purposes, so we combine and change the divide into a bit shift for faster math

    def ambisonicsCalculations(audioData, speakerData, returnZero=False):
        if returnZero:
            return 0
        #audioData = [W, X, Y, Z]
        #speakerData = [sin(azimuth), cos(azimuth), sin(zenith), cos(zenith), ??speaker Constant??]
        #Calculations Here:
        return  speakerData[4]*(
                audioData[0]/1.414213 + #sqrt(2) gain factor
                speakerData[0]*audioData[1] + #sin(azimuth)*X, the length of the depth component of the position of our speaker
                speakerData[1]*audioData[2] + #cos(azimuth)*Y, the length of the horizontal component of the position of our speaker
                speakerData[2]*audioData[3]   #sin(zenith)*Z, the length of the vertical component of the position of our speaker
                )
    

    # normalizationMultiplier = [np.float64(ambvolume)]
    # def audioNormalizationAmbisonics(audioData, volume):
    #     wVals = [] # gather all W sample values
    #     for i in range(0, len(audioData), FRAME_SIZE_IN_BYTES):
    #         wVals.append(abs(int.from_bytes(audioData[i:i+2], byteorder='little', signed=True)))

    #     MAX_POSSIBLE = 35565 #maximum possible value for the inputted data's type
    #     MAX_ALLOWED_VOLUME = MAX_POSSIBLE*volume
    #     maxOccuringValue = max(audioData)
    #     volumeDifference = maxOccuringValue-MAX_ALLOWED_VOLUME
    #     if(volumeDifference > 0): 
    #         normalizationMultiplier[0] -= (maxOccuringValue/MAX_POSSIBLE)
    #     else:
    #         normalizationMultiplier[0] += (volume-normalizationMultiplier[0])*2 #Should be mathematically... sound. ba dum tsss.


    #     print(round(number=normalizationMultiplier[0], ndigits= 5))
    #     return changeVolumeAmbisonics(audioData=audioData, volume= normalizationMultiplier[0])


    def playAudioChannel(speed=1):
        # Initialize PyAudio
        p = pyaudio.PyAudio()
        # Open a stream to sound card with the callback function
        # CHANNELS Untested for values besides 8 and 2
        stream = p.open(format=8, #paInt16 = 8 
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

    updateSpeakerList()
    print(speakerList)
    playAudioChannel(speed)
    #end of playAmbisonics()

playAmbisonics(wav_file, ambvolume=.1, speed=1)
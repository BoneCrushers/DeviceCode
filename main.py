import pyaudio
import numpy as np
import os
import math

# Initializing wav file
wav_file = os.getcwd()+"\\SoundFiles\\"+      "Chicago_Amb_Elevated_Train_B-Format_44.1_16.wav"

# Speakers. Input speakers as a list of ORIGIN VALUES, as though you were facing 0:0
# (Azimuth angle, Zenith angle, Speaker Constant, Channel number)
# In this code, this length will be assumed to be either 2 or 8. testing with odd numbers or greater 
# than 8 channels will likely cause a lot of problems with deciding where to map channels, etc
# todo? map channels in a different order than list's order? Is this necessary?
# todo? 

#   (Azimuth angle, Zenith angle, Speaker Constant, Channel number)      
#   ******  v  EDIT ME  v  ******
SPEAKER_INFORMATION = [
    [90, 0, 1, 1],
    [270, 0, 1, 2],
    [],
    [],
    [],
    [],
    [],
    []
]

# speakerList will contain an editable version of all the starting information.
# (for use in combination with accelerometer later. If accelerometer returns true angles,
# then we need a secondary copy to compute changes, if it returns changes since last report, will
# just need to update each time we get that set of data and can remove copy) 
# Only changes should be to speakerList[0] and [1] during runtime,
# and 
# (LATER) todo? replace speakerList with accelerometer calculation using stored current angle and base offset?

# NEED INFO: RADIANS OR DEGREES FOR SIN() AND COS()
# Decision: Should we store data in speakerList as degrees, or should we store the coefficient for the
# equations? Less calculations on runtime for the latter, but also less versatile if we need the angles
# for anything we havent found/thought of yet.
speakerList = SPEAKER_INFORMATION.copy()

def playAmbisonics(ambFile, ambvolume=.1, speed=1):

    #Open the file
    amb = open(ambFile, 'rb')
    fileHeader = amb.readline() + amb.readline(17)
    FILE_SIZE = int.from_bytes(fileHeader[4:8], byteorder='little')
    DATA_SIZE = int.from_bytes(fileHeader[40:44], byteorder='little')
    # CONSTANTS BASED ON FILE 
    TEST_SIZE = fileHeader[4:8] 
    FRAME_SIZE_IN_BYTES = int.from_bytes(fileHeader[32:34], byteorder='little')
    FRAME_RATE = int.from_bytes(fileHeader[24:28], byteorder='little')
    CHANNEL_COUNT = int.from_bytes(fileHeader[22:24], byteorder='little')
    VALID_BITS_PER_SAMPLE = int.from_bytes(fileHeader[36:38], byteorder='little')
    # VALID_BITS_PER_SAMPLE is incorrect? 
    SUBFORMAT_GUID = fileHeader[42:58]
    print("SUBFORMAT_GUID", SUBFORMAT_GUID)
    

    def changeVolumeAmbisonics(audioData, volume):
        dataArray = np.frombuffer(audioData, dtype=np.int16)
        newAudio = (dataArray * volume).astype(np.int16)
        return newAudio.tobytes()

    def audioCallbackAmbisonics(inData, frameCount, timeInfo, status):
        audioData = amb.read(frameCount*FRAME_SIZE_IN_BYTES) 
        returnData = bytearray()
        audioData = changeVolumeAmbisonics(audioData, ambvolume)

        #adByteStart is the counter to track where in audioData we currently are
        adByteStart=0
        for i in range(frameCount):
            #WorkingData holds 1 frame of data, stored as 16 bit integers in 4 slots, 
            #each corresponding to a channel WXYZ
            workingData = [
                int.from_bytes(audioData[adByteStart  :adByteStart+2], byteorder='little'),
                int.from_bytes(audioData[adByteStart+2:adByteStart+4], byteorder='little'),
                int.from_bytes(audioData[adByteStart+4:adByteStart+6], byteorder='little'),
                int.from_bytes(audioData[adByteStart+6:adByteStart+8], byteorder='little')
                ]
            # Iterates the speaker list. If a speaker is an empty list, we just append two 0 bytes (for balancing channel numbers),
            # else we append our ambisonics algorithm for determining sound output of the speaker based on angles provided.
            for s in speakerList:
                if(len(s) == 0):
                    channel = ambisonicsCalculations(workingData, s, returnZero=True)
                else:
                    channel = ambisonicsCalculations(workingData, s)

                returnData.extend([channel%256, channel//256])
            
            adByteStart += 8



        if(len(audioData) < frameCount*FRAME_SIZE_IN_BYTES):
            return bytes(returnData[0:len(audioData)*2]), pyaudio.paComplete

        return bytes(returnData), pyaudio.paContinue

    def ambisonicsCalculations(audioData, speakerData, returnZero=False):
        if returnZero:
            return 0
        sample = audioData[0]
        #audioData = [W, X, Y, Z]
        #speakerData = (Azimuth angle, Zenith angle, Speaker Constant, Channel number)
        #Calculations Here:
        sample =   speakerData[2]   *( 
                                    audioData[0] +
                                    math.sin(speakerData[0])*audioData[1] +
                                    math.cos(speakerData[0])*audioData[2] +
                                    math.sin(speakerData[1])*audioData[3]
                                    )
        sample = int(sample/2)
        #Testing
        print("Sample value:", sample, "Sample Class:", sample.__class__)

        #End Calculations
        return sample # return sample
    
    
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
            #in event pyaudio._portaudio poops itself, unable to edit/bugfix as it is in compiled binary.
            pass

        print("Done!")
        # Close the stream and PyAudio
        stream.stop_stream()
        stream.close()
        p.terminate()

        # Close the WAV file
        amb.close()






    playAudioChannel(speed)


playAmbisonics(wav_file, ambvolume=1)
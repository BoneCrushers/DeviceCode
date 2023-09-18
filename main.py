import pyaudio
import pyaudio._portaudio as pa
import wave
import numpy as np
import os

# Initializing wav file
wav_file = os.getcwd()+"\\SoundFiles\\"+      "Chicago_Amb_Elevated_Train_B-Format_44.1_16.wav"

def playAmbisonics(ambFile, ambvolume=.1, speed=1):

    #Open the file
    amb = open(wav_file, 'rb')
    fileHeader = amb.readline(44)
    fileHeaderPT2 = amb.readline((int.from_bytes(fileHeader[36:40], byteorder='little'))+100)
    print("data start?",int.from_bytes(fileHeader[36:40], byteorder='big'))
    print("len(fileHeader)",len(fileHeader))
    print("len(fileHeaderPT2)",len(fileHeaderPT2))
    # CONSTANTS BASED ON FILE 
    TEST_SIZE = fileHeader[4:8] # Should be near 6.42 MB
    print("FileSize", int.from_bytes(TEST_SIZE, byteorder='little'))
    FRAME_SIZE_IN_BYTES = int.from_bytes(fileHeader[32:34], byteorder='little')
    print("FrameSizeInBytes", FRAME_SIZE_IN_BYTES)
    FRAME_RATE = int.from_bytes(fileHeader[24:28], byteorder='little')
    print("FrameRate", FRAME_RATE)
    CHANNEL_COUNT = int.from_bytes(fileHeader[22:24], byteorder='little')
    print("ChannelCount", CHANNEL_COUNT)
    
    print(fileHeader)
    print(fileHeaderPT2)
    counter = 0

    def changeVolumeAmbisonics(audioData, volume):
        print(audioData)
        dataArray = np.frombuffer(audioData, dtype=np.int16)
        newAudio = (dataArray * volume).astype(np.int16)
        return newAudio.tobytes()

    def audioCallbackAmbisonics(inData, frameCount, timeInfo, status):
        audioData = amb.readline(frameCount*FRAME_SIZE_IN_BYTES)
        audioData = changeVolumeAmbisonics(audioData, ambvolume)
        returnData = []
        #adByteStart is the counter to track where in audioData we currently are
        adByteStart=0
        for i in range(frameCount):
            adByteEnd = adByteStart+FRAME_SIZE_IN_BYTES
            workingData = audioData[adByteStart:adByteEnd]
            #workingData now holds 1 frame of INPUT data, does not match size of output.
            #stored as [0:2] = 2-bytes channel W, [2:4] = 2-bytes channel X, ...
            #channel1
            returnData.append(bytes(
                workingData[0:2]# + workingData[2:4] + workingData[4:6] + workingData[6:8]
                ))
            #channel2
            returnData.append(bytes(
                workingData[0:2]# + workingData[2:4] + workingData[4:6] + workingData[6:8]
                ))
            #channel3
            returnData.append(bytes(
                workingData[0:2]# + workingData[2:4] + workingData[4:6] + workingData[6:8]
                ))
            #channel4
            returnData.append(bytes(
                workingData[0:2]# + workingData[2:4] + workingData[4:6] + workingData[6:8]
                ))
            #channel5
            returnData.append(bytes(
                workingData[0:2]# + workingData[2:4] + workingData[4:6] + workingData[6:8]
                ))
            #channel6
            returnData.append(bytes(
                workingData[0:2]# + workingData[2:4] + workingData[4:6] + workingData[6:8]
                ))
            #channel7
            returnData.append(bytes(
                workingData[0:2]# + workingData[2:4] + workingData[4:6] + workingData[6:8]
                ))
            #channel8
            returnData.append(bytes(
                workingData[0:2]# + workingData[2:4] + workingData[4:6] + workingData[6:8]
                ))

        return returnData, pyaudio.paContinue
    
    def playAudioChannel(file=ambFile, speed=1):
        # Initialize PyAudio
        p = pyaudio.PyAudio()
        # Open a stream to sound card with the callback function
        
        stream = p.open(format=8, #paInt16 = 8, paCustomFormat = 65536 
                        channels=8,
                        rate=int(FRAME_RATE * speed),
                        output=True, 
                        stream_callback=audioCallbackAmbisonics)
        # Start the stream
        stream.start_stream()
        # print(pa.is_stream_active(pa.stream(stream)).__class__)
        while stream.is_active():
            pass
        # Close the stream and PyAudio
        stream.stop_stream()
        stream.close()
        p.terminate()

        # Close the WAV file
        amb.close()
    
    playAudioChannel()




# def changeVolume(audioData, volume):
#     dataArray = np.frombuffer(audioData, dtype=np.int16)
#     newAudio = (dataArray * volume).astype(np.int16)
#     return newAudio.tobytes()


# # Define callback function to process and adjust audio data
# def audioCallback(inData, frameCount, timeInfo, status):
#     audioData = wf.readframes(frameCount)
#     audioData = changeVolume(audioData, .1)
#     print(len(audioData))
#     print(audioData)
#     return audioData, pyaudio.paContinue


#Selecting each channel: Channels 1-8, edit first tuple *******************EDIT HERE********************
# EditMeChannelSelection = (
#     True,      #Channel 1
#     False,      #Channel 2
#     False,      #Channel 3
#     False,      #Channel 4
#     False,      #Channel 5
#     False,      #Channel 6
#     False,      #Channel 7
#     True       #Channel 8
# )

# ChannelSelect = (
#     EditMeChannelSelection[0], EditMeChannelSelection[0], EditMeChannelSelection[1], EditMeChannelSelection[1],
#     EditMeChannelSelection[2], EditMeChannelSelection[2], EditMeChannelSelection[3], EditMeChannelSelection[3],
#     EditMeChannelSelection[4], EditMeChannelSelection[4], EditMeChannelSelection[5], EditMeChannelSelection[5],
#     EditMeChannelSelection[6], EditMeChannelSelection[6], EditMeChannelSelection[7], EditMeChannelSelection[7]
#     )
# def audioCallbackChannel(inData, frameCount, timeInfo, status):
#     audioData = wf.readframes(frameCount)
#     audioData = changeVolume(audioData, .05)
#     editedAudioData = []
#     #Select Channels here, 0-7 with each channel being 2 T/F, enter the channels you wish to select as a tuple of T/F
#     #Note: know your input for now, selecting the wrong number of channels will output unintentended data
#     #TESTING NOTES:
#     #CHANNEL SEPARATION:
#         # 7.1 Audio Standard: (Look at again with results below, may map differently than believed)
#         # 1 = Left
#         # 2 = Right
#         # 3 = Center
#         # 4 = LFE
#         # 5 = Side Left
#         # 6 = Side Right
#         # 7 = Back Left
#         # 8 = Back Right

#         #Testing: Made significant progress since talking with Flint
#         #       Does not directly translate, IE 1/3 mixes up bits and plays bad audio to 4 channels, L/R Front *and* L/R back
#         #   1/2: Left side only Front plug, Normal Volume; left side only Back plug, Normal Volume
#         #   3/4: Right side only Front plug, Normal Volume; right side only Back plug, Normal Volume
#         #   5/6: Left side only Surround plug, Normal Volume; left side only Center plug, Normal Volume
#         #   7/8: Right side only Surround plug, Normal Volume; right side only Center plug, Normal Volume


# #lOOK AT Portaudio check and see if it does anything on its own
# # Configure soundcard with 

#     ad = iter(audioData)
#     try:
#         # 'i' is a counter for bytes, equal to how large the finalized data array should be.
#         # used as a filter to select which channels we want to put our useful data on.
#         BYTES_PER_INTEGER = 2
#         CHANNEL_COUNT = 8
#         FRAME_SIZE_IN_BYTES = BYTES_PER_INTEGER*CHANNEL_COUNT
#         for i in range(frameCount*FRAME_SIZE_IN_BYTES):
#             # Input data into selected channel, with zeroes in the other  channels
#             if(ChannelSelect[i%CHANNEL_COUNT*2]):
#                 editedAudioData.append(int(next(ad)))
#             elif(ChannelSelect[i%CHANNEL_COUNT*2] == False):
#                 editedAudioData.append(0)
#             else:
#                 editedAudioData.append(0)
#                 next(ad)
#     except StopIteration:
#         pass
    
#     returnData = bytes(editedAudioData)
#     return returnData, pyaudio.paContinue


# def playAudio(file, speed=1):
#     # Initialize PyAudio
#     p = pyaudio.PyAudio()
#     # Open a stream to sound card with the callback function
#     stream = p.open(format=8, #p.get_format_from_width(wf.getsampwidth())
#                     channels=wf.getnchannels(),
#                     rate=int(wf.getframerate() * speed),
#                     output=True,
#                     stream_callback=audioCallback)
#     # Start the stream
#     stream.start_stream()
#     while stream.is_active():
#         pass
#     # Close the stream and PyAudio
#     stream.stop_stream()
#     stream.close()
#     p.terminate()

#     # Close the WAV file
#     wf.close()

# def playAudioChannel(file, speed=1):
#     # Initialize PyAudio
#     p = pyaudio.PyAudio()
#     # Open a stream to sound card with the callback function
#     stream = p.open(format=pyaudio.get_format_from_width(wf.getsampwidth()), 
#                     channels=8,
#                     rate=int(wf.getframerate() * speed),
#                     output=True, 
#                     stream_callback=audioCallbackChannel)
#     # Start the stream
#     stream.start_stream()
#     while stream.is_active():
#         pass
#     # Close the stream and PyAudio
#     stream.stop_stream()
#     stream.close()
#     p.terminate()

#     # Close the WAV file
#     wf.close()



playAmbisonics(wav_file, ambvolume=.1, speed=1)

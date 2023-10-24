import pyaudio
import numpy as np
import os
import struct
import math

class PlayAmbisonics():
    def __init__(self, fileName, speakerData, ambvolume=.1, speed=1, playImmediately=True):
        wav_file = os.getcwd()+"\\SoundFiles\\"+   fileName
        amb = open(wav_file, 'rb')
        self.fileHeader = amb.read(16)
        self.ambFileData= self.fileHeader+amb.read(int.from_bytes(self.fileHeader[4:8], byteorder='little', signed=False)-16)
        amb.close()
        
        self.OUTPUT_CHANNEL_COUNT = 0
        self.SPEAKER_INFORMATION = []
        self.updateSpeakerInformation(speakerData)
        self.speakerList = []
        self.updateSpeakerList(speakerData)

        formatString = '4sL4s4sLHHLLHH4s'
        """
        File (RIFF), File Size, File type (WAVE), Format chunk marker(fmt ),
        Length of format Data, Format Type, # Channels, Sample Rate, bits/sec,
        idk what the use here is, bits/sample, DATA header *OR* Subformat Data/Metadata
        """
        self.unpackedHeader = struct.unpack(formatString, self.ambFileData[0:struct.calcsize(formatString)])
        self.IN_CHANNEL_COUNT = self.unpackedHeader[6]
        self.FRAME_SIZE_IN_BYTES = self.unpackedHeader[9]
        self.FRAME_RATE = self.unpackedHeader[7]
        self.ambFileCurPosition = [self.ambFileData.find(b'data')+4]

        self.normalizationMultiplier = [np.float64(ambvolume)]

        if(playImmediately):
            self.playAudioChannel(speed)


    

    
    def getNextData(self, ambFileData, size, movePointer=True):
        if(movePointer): self.ambFileCurPosition[0] += size
        return np.frombuffer(ambFileData[self.ambFileCurPosition[0]-size:self.ambFileCurPosition[0]], dtype=np.int16)
    
    
    #FINISH
    def updateSpeakerList(self, data):
        self.speakerList = [[],[],[],[],[],[],[],[]]
        self.OUTPUT_CHANNEL_COUNT = 0
        for i in range(len(self.SPEAKER_INFORMATION)):
            if len(self.SPEAKER_INFORMATION[i]) == 3:
                self.speakerList[i] = [math.sin(self.SPEAKER_INFORMATION[i][0]), math.cos(self.SPEAKER_INFORMATION[i][0]), math.sin(self.SPEAKER_INFORMATION[i][1]), math.cos(self.SPEAKER_INFORMATION[i][1]), self.SPEAKER_INFORMATION[i][2]]
                self.OUTPUT_CHANNEL_COUNT += 1
            else:
                self.speakerList[i] = []
    
    #FINISH?
    def updateSpeakerInformation(self, data):
        """
        Format: [Theta angle(rad), Zenith angle(rad), SpeakerConstant, Data Line (0-7)] for EACH SPEAKER
        """
        self.SPEAKER_INFORMATION = [[],[],[],[],[],[],[],[]]
        for d in data:
            if(len(d)==4):
                if(len(self.SPEAKER_INFORMATION[d[3]]) != 0):
                    raise AmbisonicsError("Cannot have multiple speakers on the same line.")
                elif(d[3] > 7 or d[3] < 0):
                    raise AmbisonicsError("Datalines must be between 0 and 7.")
                else:
                    self.SPEAKER_INFORMATION[d[3]] = d[0:3]
            else:
                raise AmbisonicsError("All Speakers must have 4 pieces of data: [Theta angle(rads), Zenith angle(rads), SpeakerConstant, Data Line (0-7)]")
                
        
    
    def audioCallbackAmbisonics(self, inData, frameCount, timeInfo, status):
        AD = self.getNextData(self.ambFileData, frameCount*self.FRAME_SIZE_IN_BYTES)
        AD = np.ndarray((int(len(AD)/self.IN_CHANNEL_COUNT), self.IN_CHANNEL_COUNT), dtype=AD.dtype, buffer=AD)
        audioData = AD.T

        RD = np.zeros((int(len(audioData[0])), self.OUTPUT_CHANNEL_COUNT), dtype=np.int16)
        returnData = RD.T 
        
        #AudioData = [Z, X, W, Y]? What is up with this order?
        #SpeakerList[i] = [sin(azimuth), cos(azimuth), sin(zenith), cos(zenith)]
        # sin(A)*y, cos(A)*x, sin(z)*z
        for i in range(self.OUTPUT_CHANNEL_COUNT):
            returnData[i] = self.speakerList[i][4]*(
                audioData[2] + 
                self.speakerList[i][0]*audioData[3] + 
                self.speakerList[i][1]*audioData[1] + 
                self.speakerList[i][2]*audioData[0]   
                )*self.normalizationMultiplier[0]
            """
            Notes:
            the clipping is only on one side, I believe it was when values were negative.
            When the same audio signal was played on the opposite side (ie the values switched from 
            positive to negative and we swap between clipping and no clipping.)
            ***look in to order and possible data cutting during conversion?***

            take in different direction:
            make a gui that can place a mono audio signal and place it somewhere in space
            third person
            circle for 2D, sliders for volume and z axis
            transducer toggle, 
            """
        return RD.tobytes(), pyaudio.paContinue
            

    
    def audioNormalizationAmbisonics(self, wVals, volume):
        MAX_POSSIBLE = 35565 #maximum possible value for the inputted data's type
        MAX_ALLOWED_VOLUME = MAX_POSSIBLE*volume
        maxOccuringValue = max(max(wVals)*self.normalizationMultiplier[0], -1*(min(wVals)*self.normalizationMultiplier[0]))
        volumeDifference = (maxOccuringValue-MAX_ALLOWED_VOLUME)/MAX_POSSIBLE
        #normalizationMultiplier should always be greater than volumeDifference, both values expected to be between 0 and 1
        if(volumeDifference > 0):
            self.normalizationMultiplier[0] -= volumeDifference/2 #add multiplier/exponential factor? of some kind?
        else:
            self.normalizationMultiplier[0] += (volume-self.normalizationMultiplier[0])/4

        #TEST
        print(round(number=self.normalizationMultiplier[0], ndigits= 5))
        return


    def playAudioChannel(self, speed=1):
        # Initialize PyAudio
        p = pyaudio.PyAudio()
        # Open a stream to sound card with the callback function
        # CHANNELS Untested for values besides 8 and 2
        stream = p.open(format=8, #paInt16 = 8 
                        channels=self.OUTPUT_CHANNEL_COUNT,
                        rate=int(self.FRAME_RATE * speed),
                        output=True, 
                        stream_callback=self.audioCallbackAmbisonics)

        #TEST
        print("Start!")

        stream.start_stream()
        try:
            while stream.is_active():
                pass
        except ValueError:
            print("ValueError")
            stream.stop_stream()
            stream.close()
            p.terminate()
        stream.stop_stream()
        stream.close()
        p.terminate()

        #TEST - can I actually do this?
        del(self)
        print("Done!")


    

class AmbisonicsError(Exception):
    def __init__(self, message):
        super().__init__(message)

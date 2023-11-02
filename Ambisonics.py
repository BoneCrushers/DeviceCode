import pyaudio
import numpy as np
import os
import struct
import tkinter as tk
from tkinter import ttk
import GUI
import AmbisonicsGUI
import traceback



class PlayAmbisonics():
    def __init__(self, fileName, speakerData, ambvolume=.1, speed=1):
        wav_file = os.getcwd()+"\\SoundFiles\\"+   fileName
        amb = open(wav_file, 'rb')
        self.fileHeader = amb.read(16)
        self.ambFileData= self.fileHeader+amb.read(int.from_bytes(self.fileHeader[4:8], byteorder='little', signed=False)-16)
        amb.close()
        

        self.OUTPUT_CHANNEL_COUNT = 8
        self.AMBISONICS_INPUT_CHANNEL_COUNT = 4
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
        self.speed = speed

        # Initialize PyAudio
        self.p = pyaudio.PyAudio()

    
    def __init__(self, window, speakerData, fileName="Center.wav", ambvolume=.1, speed=1):
        """
        For use through a window.
        """
        wav_file = os.getcwd()+"\\SoundFiles\\"+   fileName
        amb = open(wav_file, 'rb')
        self.fileHeader = amb.read(16)
        self.ambFileData= self.fileHeader+amb.read(int.from_bytes(self.fileHeader[4:8], byteorder='little', signed=False)-16)
        amb.close()
        formatString = '4sL4s4sLHHLLHH4s'
        """
        unpackedHeader format:
        File (RIFF), File Size, File type (WAVE), Format chunk marker(fmt ),
        Length of format Data, Format Type, # Channels, Sample Rate, bits/sec,
        idk what the use here is, bits/sample, DATA header *OR* Subformat Data/Metadata
        """
        self.unpackedHeader = struct.unpack(formatString, self.ambFileData[0:struct.calcsize(formatString)])
        self.IN_CHANNEL_COUNT = self.unpackedHeader[6]
        self.FRAME_SIZE_IN_BYTES = self.unpackedHeader[9]
        self.FRAME_RATE = self.unpackedHeader[7]
        self.ambFileCurPosition = self.ambFileData.find(b'data')+4
        self.ambFileStartPosition = self.ambFileData.find(b'data')+4
        self.ambFileEndPosition = int.from_bytes(self.fileHeader[4:8], byteorder='little', signed=False)


        self.OUTPUT_CHANNEL_COUNT=8
        self.AMBISONICS_INPUT_CHANNEL_COUNT = 4
        self.SPEAKER_INFORMATION = []
        self.updateSpeakerInformation(speakerData)
        self.speakerList = []
        self.updateSpeakerList(speakerData)

        self.window = window
        self.soundLocationData = self.window.getAngleData()

        self.normalizationMultiplier = [np.float64(ambvolume)]
        self.speed = speed

        # Initialize PyAudio
        self.p = pyaudio.PyAudio()
        


    
    def getNextData(self, FileData: str, size, movePointer=True):
        """
        Gets the next 'size' bytes of data, converting them into np.int16
        :FileData: stream of data
        :return: np.ndarray
        """
        if(movePointer): self.ambFileCurPosition += size
        temp = np.frombuffer(FileData[self.ambFileCurPosition-size:self.ambFileCurPosition], dtype=np.int16)
        if(self.IN_CHANNEL_COUNT == 1):
            return self.placeMonoAudio(temp)
        else:
            return temp
    
    #FINISH
    def updateSpeakerList(self, data):
        """
        input is list of 3 or 0 item lists, 0 is no speaker, format [theta, zenith, coefficient]
        Updates the each speaker's sin/cos for use in calculation phase during playback
        :return: None
        """
        self.speakerList = [[],[],[],[],[],[],[],[]]
        for i in range(len(self.SPEAKER_INFORMATION)):
            if len(self.SPEAKER_INFORMATION[i]) == 3:
                self.speakerList[i] = [np.sin(self.SPEAKER_INFORMATION[i][0]), np.cos(self.SPEAKER_INFORMATION[i][0]), np.sin(self.SPEAKER_INFORMATION[i][1]), np.cos(self.SPEAKER_INFORMATION[i][1]), self.SPEAKER_INFORMATION[i][2]]
            else:
                self.speakerList[i] = []
                # self.get #WHAT IS LINE HERE FOR?
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

    def updateSoundLocationData(self):
        """
        Updates location data from window's current data
        """
        self.soundLocationData = self.window.getAngleData()

    def placeMonoAudio(self, data):
        formattedData = np.frombuffer(data, dtype=np.int16)
        arr = np.ndarray((len(formattedData), 4), dtype=np.int16)
        arrT = arr.T
        
        arrT[0] = formattedData
        arrT[1] = np.cos(self.soundLocationData[0])*formattedData*self.soundLocationData[2]
        arrT[2] = np.sin(self.soundLocationData[0])*formattedData*self.soundLocationData[2]
        arrT[3] = np.sin(self.soundLocationData[1])*formattedData*self.soundLocationData[2]
        return arr.flatten()
        
    
    def audioCallbackAmbisonics(self, inData, frameCount, timeInfo, status):
        #TEST
        print("called", self.ambFileCurPosition)
        AD = self.getNextData(self.ambFileData, frameCount*self.FRAME_SIZE_IN_BYTES)
        AD = np.ndarray((int(len(AD)/self.AMBISONICS_INPUT_CHANNEL_COUNT), self.AMBISONICS_INPUT_CHANNEL_COUNT), dtype=AD.dtype, buffer=AD)
        audioData = AD.T

        RD = np.zeros((int(len(audioData[0])), self.OUTPUT_CHANNEL_COUNT), dtype=np.int16)
        returnData = RD.T 
        
        #AudioData = [Z, X, W, Y]? What is up with this order?
        #SpeakerList[i] = [sin(azimuth), cos(azimuth), sin(zenith), cos(zenith)]
        # sin(A)*y, cos(A)*x, sin(z)*z
        for i in range(self.OUTPUT_CHANNEL_COUNT):
            if(len(self.speakerList[i]) != 0):
                returnData[i] = self.speakerList[i][4]*(
                    audioData[2] + 
                    self.speakerList[i][0]*audioData[3] + 
                    self.speakerList[i][1]*audioData[1] + 
                    self.speakerList[i][2]*audioData[0]   
                    )*self.normalizationMultiplier[0]
            else:
                returnData[i] = 0
            """
            Notes:
            the clipping is only on one side, I believe it was when values were negative.
            When the same audio signal was played on the opposite side (ie the values switched from 
            positive to negative and we swap between clipping and no clipping.)
            ***look in to order and possible data cutting during conversion?***
            """
        return RD.tobytes(), pyaudio.paContinue
            

    
    # def audioNormalizationAmbisonics(self, wVals, volume):
    #     MAX_POSSIBLE = 35565 #maximum possible value for the inputted data's type
    #     MAX_ALLOWED_VOLUME = MAX_POSSIBLE*volume
    #     maxOccuringValue = max(max(wVals)*self.normalizationMultiplier[0], -1*(min(wVals)*self.normalizationMultiplier[0]))
    #     volumeDifference = (maxOccuringValue-MAX_ALLOWED_VOLUME)/MAX_POSSIBLE
    #     #normalizationMultiplier should always be greater than volumeDifference, both values expected to be between 0 and 1
    #     if(volumeDifference > 0):
    #         self.normalizationMultiplier[0] -= volumeDifference/2 #add multiplier/exponential factor? of some kind?
    #     else:
    #         self.normalizationMultiplier[0] += (volume-self.normalizationMultiplier[0])/4

    #     #TEST
    #     print(round(number=self.normalizationMultiplier[0], ndigits= 5))
    #     return

    def startAudioChannel(self, speed=1):
        #TEST
        print(self.ambFileStartPosition, self.ambFileCurPosition)
        self.stream = self.p.open(format=8, #paInt16 = 8 
                        channels=self.OUTPUT_CHANNEL_COUNT,
                        rate=int(self.FRAME_RATE * speed),
                        output=True, 
                        stream_callback=self.audioCallbackAmbisonics)
        
        #TEST
        print("Start!")
        self.ambFileCurPosition = self.ambFileStartPosition
        self.stream.start_stream()

    def stopAudioChannel(self):
        self.ambFileCurPosition = self.ambFileEndPosition
        self.stream.stop_stream()
        self.stream.close()

        #TEST
        print("Done!")

        
    

class AmbisonicsError(Exception):
    def __init__(self, message):
        super().__init__(message)

class AmbEndOfFileError(Exception):
    def __init__(self, message=None):
        super().__init__(message)

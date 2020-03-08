import os
import time
import string
import requests
import textwrap
import bluetooth
import numpy as np
import pandas as pd
from mindwavemobile.MindwaveDataPoints import *
from mindwavemobile.MindwaveDataPointReader import MindwaveDataPointReader

pandasData = ''
URL = 'http://44.233.139.129:8000/eeg/'

def stringParsing():
    if pandasData is None:
        print('Usage : stringParsing(string value)')
        os.exit(-1)

    retList = pandasData.split(':')

    for i in range(0,len(retList)):
        retList[i] = retList[i].strip('ABCDEFGHIJKLMNOPQRSTUVWXYZ\nabcedfghijklmnopqrstuvwxyz ')
    retList = list(filter(None,retList))
    now = time.localtime()
    time_str = str(now.tm_year) + '.' + str(now.tm_mon) + '.' + str(now.tm_mday) + '.' + str(now.tm_hour) + '.' + str(now.tm_min) + '.' + str(now.tm_sec)
    retList.insert(0,time_str)
    #retList.insert(0,str(time.now()))
    return retList

if __name__ == '__main__': # main function
    pandasList = []
    tempList = []
    poor_num = 0
    dataPos = 0
    dataRaw = 0
    dataFrame = pd.DataFrame(columns=['Time','delta','theta','lowAlpha','highAlpha','lowBeta','highBeta','lowGamma','midGamma','Meditation','Attention'])
    rawFrame = pd.DataFrame(columns=['Time','RawValue'])
    mindwaveDataPointReader = MindwaveDataPointReader() # make a data reader object
    mindwaveDataPointReader.start() # connect with MindWave Mobile 2
    #time.sleep(3)

    if(mindwaveDataPointReader.isConnected()):
        data = {'MAC':'C4:64:E3:E8:E6:7B'}
        #response = requests.post(URL,data=data)
        try:
            while(True):
                dataPoint = mindwaveDataPointReader.readNextDataPoint()
                if(not dataPoint.__class__ is RawDataPoint):
                    if(dataPoint.__class__ is PoorSignalLevelDataPoint):
                        poor_num = dataPoint.amountOfNoise
                        #print(dataPoint.amountOfNoise)

                    if(poor_num < 200 and dataPoint.__class__ is EEGPowersDataPoint):
                        if(not dataPoint.is_valid()):
                            continue

                        pandasData = str(dataPoint)
                        pandasList = stringParsing()
                        pandasList.extend(tempList)
                        #pandasList = pandasList + temp_list
                        #temp_list.clear()
                        dataFrame.loc[dataPos] = pandasList
                        dataPos += 1
                        #print(pandasList)
                        print(dataFrame)

                    if(poor_num < 200 and dataPoint.__class__ is MeditationDataPoint):
                        tempList.clear()
                        tempList.append(str(dataPoint.meditationValue))

                    if(poor_num < 200 and dataPoint.__class__ is AttentionDataPoint):
                        tempList.append(str(dataPoint.attentionValue))

                    #if(poor_num < 200 and dataPoint.__class__ is BlinkDataPoint):
                    #    print('BlinkDataPoint')
                    #    print(dataPoint)
                #else:
                    '''
                    now = time.localtime()
                    time_str = str(now.tm_year) + '.' + str(now.tm_mon) + '.' + str(now.tm_mday) + '.' + str(now.tm_hour) + '.' + str(now.tm_min) + '.' + str(now.tm_sec)
                    rawList = []
                    rawList.insert(0,time_str)
                    rawList.insert(1,str(dataPoint.rawValue))
                    rawFrame.loc[dataRaw] = rawList
                    dataRaw += 1
                    '''

        except KeyboardInterrupt as interrupt:
            print(interrupt)
            mindwaveDataPointReader.close()
            dataFrame.to_csv('Result.csv',mode='w',header=True)
            rawFrame.to_csv('RawValue.csv',mode='w',header=True)
    else:
        print((textwrap.dedent("""\
            Exiting because the program could not connect
            to the Mindwave Mobile device.""").replace("\n", " ")))

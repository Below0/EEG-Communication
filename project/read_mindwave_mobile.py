import os
import time
import string
import requests
import textwrap
import bluetooth
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from sklearn import svm
from SupportVectorMachine import SupportVectorMachine as svmFunctions
from MLP_v1 import MultiLayerPerceptron as mplFunctions # MPL
from sklearn.model_selection import train_test_split, GridSearchCV
from mindwavemobile.MindwaveDataPoints import *
from mindwavemobile.MindwaveDataPointReader import MindwaveDataPointReader

pandasData = ''
user = 'Unknown'
normalFile = 'normal.csv'
emergencyFile = 'scared.csv'
URL = 'http://44.233.139.129:8000/eeg/'
isTrain = False

def stringParsing():
    if pandasData is None:
        print('Usage : stringParsing(string value)')
        os.exit(-1)

    retList = pandasData.split(':')

    for i in range(0,len(retList)):
        retList[i] = retList[i].strip('ABCDEFGHIJKLMNOPQRSTUVWXYZ\nabcedfghijklmnopqrstuvwxyz ')
    retList = list(filter(None,retList))
    #now = time.localtime()
    #time_str = str(now.tm_year) + '.' + str(now.tm_mon) + '.' + str(now.tm_mday) + '.' + str(now.tm_hour) + '.' + str(now.tm_min) + '.' + str(now.tm_sec)
    #retList.insert(0,time_str)
    #retList.insert(0,str(time.now()))
    return retList

if __name__ == '__main__': # main function
    tempList = []
    pandasList = []
    poor_num = 0
    dataPos = 0
    dataRaw = 0
    dataFrame = pd.DataFrame(columns=['delta','theta','lowAlpha','highAlpha','lowBeta','highBeta','lowGamma','midGamma','Meditation','Attention'])
    dataFrame.set_index('delta') # let 'delta' be an index
    rawFrame = pd.DataFrame(columns=['Time','RawValue'])
    user = input('write an user name : ')
    user = str(user)

    isTrain = input('The data is trained? : (Y/N)')
    isTrain = str(isTrain)

    if(isTrain is 'Y' or isTrain is 'y'):
        isTrain = True
    else:
        isTrain = False

    mplTest = mplFunctions() # make a MPL object
    mplTest._readDataFromFile(emergencyFile,normalFile)
    mplTest._trainDataFromValue(isTrain)
    print('MPL test finished...')
    mindwaveDataPointReader = MindwaveDataPointReader() # make a data reader object
    mindwaveDataPointReader.start() # connect with MindWave Mobile 2

    if(mindwaveDataPointReader.isConnected()):
        data = {'address':'C4:64:E3:E8:E6:7B','name':'테스트'}
        #response = requests.post(URL,data=data)
        try:
            while(True):
                dataPoint = mindwaveDataPointReader.readNextDataPoint()
                if(not dataPoint.__class__ is RawDataPoint):
                    if(dataPoint.__class__ is PoorSignalLevelDataPoint):
                        poor_num = dataPoint.amountOfNoise

                    if(poor_num < 200 and dataPoint.__class__ is EEGPowersDataPoint):
                        if(not dataPoint.is_valid()):
                            continue

                        pandasData = str(dataPoint)
                        pandasList = stringParsing()
                        pandasList.extend(tempList)
                        tempFrame = pd.DataFrame(columns=['delta','theta','lowAlpha','highAlpha','lowBeta','highBeta','lowGamma','midGamma','Meditation','Attention'])
                        tempFrame.set_index('delta')
                        tempFrame.loc[0] = pandasList
                        mplTest._extractResult(tempFrame,isTrain)
                        print(tempFrame)
                        dataFrame.loc[dataPos] = pandasList
                        dataPos += 1
                        #print(dataFrame)

                    if(poor_num < 200 and dataPoint.__class__ is MeditationDataPoint):
                        tempList.clear()
                        tempList.append(str(dataPoint.meditationValue))

                    if(poor_num < 200 and dataPoint.__class__ is AttentionDataPoint):
                        tempList.append(str(dataPoint.attentionValue))

        except KeyboardInterrupt as interrupt:
            print(interrupt)
            mindwaveDataPointReader.close()
            now = time.localtime()
            time_str = str(now.tm_year)+'_'+str(now.tm_mon)+'_'+str(now.tm_mday)+'_'+str(now.tm_hour)+'_'+str(now.tm_min)
            realTimeFile = user + '_' + time_str + '.csv'
            dataFrame.to_csv(realTimeFile,mode='w',header=True)
    else:
        print((textwrap.dedent("""\
            Exiting because the program could not connect
            to the Mindwave Mobile device.""").replace("\n", " ")))

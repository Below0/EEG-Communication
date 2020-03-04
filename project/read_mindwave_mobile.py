import os
import time
import string
import textwrap
import bluetooth
import numpy as np
import pandas as pd
from mindwavemobile.MindwaveDataPoints import *
from mindwavemobile.MindwaveDataPointReader import MindwaveDataPointReader

pandasData = ''

def stringParsing():
    if pandasData is None:
        print('Usage : stringParsing(string value)')
        os.exit(-1)

    retList = pandasData.split(':')

    for i in range(0,len(retList)):
        retList[i] = retList[i].strip('ABCDEFGHIJKLMNOPQRSTUVWXYZ\nabcedfghijklmnopqrstuvwxyz ')
    retList = list(filter(None,retList))

    return retList

if __name__ == '__main__': # main function
    poor_num = 0
    dataPos = 0
    dataFrame = pd.DataFrame(columns=['delta','theta','lowAlpha','highAlpha','lowBeta','highBeta','lowGamma','midGamma'])
    mindwaveDataPointReader = MindwaveDataPointReader() # make a data reader object
    mindwaveDataPointReader.start() # connect with MindWave Mobile 2
    #time.sleep(3)

    if(mindwaveDataPointReader.isConnected()):
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
                        dataFrame.loc[dataPos] = pandasList
                        dataPos += 1
                        #print(pandasList)
                        print(dataFrame)

                    elif((dataPoint.__class__ is not EEGPowersDataPoint) and (dataPoint.__class__ is not PoorSignalLevelDataPoint)):
                        print(dataPoint)
        except KeyboardInterrupt as interrupt:
            print(interrupt)
            mindwaveDataPointReader.close()
            dataFrame.to_csv('Result.csv',mode='w',header=True)
    else:
        print((textwrap.dedent("""\
            Exiting because the program could not connect
            to the Mindwave Mobile device.""").replace("\n", " ")))

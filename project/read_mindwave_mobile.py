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
from MLP import MultiLayerPerceptron as mplFunctions # MPL
from sklearn.model_selection import train_test_split, GridSearchCV
from mindwavemobile.MindwaveDataPoints import *
from mindwavemobile.MindwaveDataPointReader import MindwaveDataPointReader

pandasData = ''
user = 'Unknown'
emergencyFile = 'Result_per_second.csv'
normalFile = 'Result_game.csv'
URL = 'http://44.233.139.129:8000/eeg/'

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
    mplTest = mplFunctions() # make a MPL object
    mplTest._readDataFromFile(emergencyFile,normalFile)
    mplTest._trainDataFromValue()
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
                        printout = mplTest._extractResult(tempFrame)
                        dataFrame.loc[dataPos] = pandasList
                        dataPos += 1
                        print(dataFrame)

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

            '''
            # Make an class object and Read data
            svmTest = svmFunctions()
            x,labels = svmTest._readDataFromFile(normalFile,currentStatus)

            # Split data to train and test on 80-20 ratio
            X_train,X_test,y_train,y_test = train_test_split(x,labels,test_size = 0.2,random_state=0)
            # Regularization
            X_train,X_test = svmTest._trainRegularization(X_train,X_test)
            y_train,y_test = svmTest._trainRegularization(y_train,y_test)

            print("Displaying data. Close window to continue.")
            # Plot data
            svmTest._plotData(X_train,y_train,X_test,y_test)

            # make a classifier and fit on training data
            clf = svm.SVC(kernel='linear',C=10000,random_state=0)

            # Train classifier
            clf.fit(X_train, y_train)
            print("Displaying decision function. Close window to continue.")
            # Plot decision function on training and test data
            #svmTest._plotDecisionFunction(X_train, y_train, X_test, y_test, clf)

            # Make predictions on unseen test data
            clf_predictions = clf.predict(X_test)
            print("Accuracy: {}%".format(clf.score(X_test, y_test)*100))
            #rawFrame.to_csv('RawValue.csv',mode='w',header=True)
            '''
    else:
        print((textwrap.dedent("""\
            Exiting because the program could not connect
            to the Mindwave Mobile device.""").replace("\n", " ")))

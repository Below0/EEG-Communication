import os
import sys
import pickle
import random
import pandas as pd, numpy as np
from keras.utils import np_utils
from keras.models import Sequential
from keras.models import load_model
from keras.callbacks import EarlyStopping
from sklearn.preprocessing import RobustScaler
from sklearn.externals import joblib
from keras.layers.core import Dense, Dropout, Activation

class MultiLayerPerceptron:

    def __init__(self):
        self._test1 = None
        self._test2 = None
        self._csv = None
        self._bclass = None
        self._scaler = None
        self._X = None # input file
        self._y = None # output file
        self._x_train = None
        self._y_train = None
        self._x_test = None
        self._y_test = None
        self._test_size = None
        self._hist = None
        self._model = None
        self._dat = None
        self._xhat = None
        self._yhat = None
        self._loss_and_metrics = None

    def _readDataFromFile(self,emergencyFile,normalFile):
        self._test1=pd.read_csv(emergencyFile)
        self._test2=pd.read_csv(normalFile)

        self._test1["label"] = "unsafe"
        self._test2["label"] = "safe"

        self._csv=pd.concat([self._test1,self._test2])
        self._test_size = int(70*(self._csv.shape[0]/100))
        self._bclass = {'safe':[1, 0],'unsafe':[0, 1]}
        self._y = np.empty((self._csv.shape[0],2))

        for i, v in enumerate(self._csv['label']):
            self._y[i] = self._bclass[v]

        del self._csv['label']

    def _trainDataFromValue(self,isTrained=False):
        #self._X = self._csv.to_numpy()
        self._X = self._csv[['delta','theta','lowAlpha','highAlpha','lowBeta','highBeta','lowGamma','midGamma','Meditation','Attention']].to_numpy()

        self._scaler = RobustScaler()
        self._scaler.fit(self._X)
        self._X = self._scaler.transform(self._X)

        tmp = [[x,y_tmp] for x, y_tmp in zip(self._X,self._y)]
        random.shuffle(tmp)
        self._X = [n[0] for n in tmp]
        self._y = [n[1] for n in tmp]

        self._X = np.asarray(self._X,dtype=np.float32)
        self._y = np.asarray(self._y,dtype=np.float32)

        self._x_train,self._y_train = self._X[1:self._test_size],self._y[1:self._test_size]
        self._x_test,self._y_test = self._X[self._test_size:],self._y[self._test_size:]

        print(self._x_train.shape,self._y_train.shape,self._x_test.shape,self._y_test.shape)

        self._model = Sequential()
        self._model.add(Dense(512,input_shape=(10,)))
        self._model.add(Activation('relu'))
        self._model.add(Dropout(0.1))
        self._model.add(Dense(512))
        self._model.add(Activation('relu'))
        self._model.add(Dropout(0.1))
        self._model.add(Dense(2))
        self._model.add(Activation('sigmoid'))
        self._model.compile(loss='binary_crossentropy',optimizer='rmsprop',metrics=['accuracy'])

        #모델 학습시키기
        if(isTrained is False):
            self._hist = self._model.fit(self._x_train,self._y_train,epochs=300,batch_size=128,validation_data=(self._x_test,self._y_test),verbose=2)
        else:
            self._scaler = joblib.load('robust_scaler.pkl')
            self._model = load_model('eeg_model.h5')
            self._model.compile(loss='binary_crossentropy',optimizer='rmsprop',metrics=['accuracy'])

    def _extractResult(self,arguList,isTrained=False):
        #arguList.drop(['Unnamed: 0'],axis=1,inplace=True)
        self._X = arguList[['delta','theta','lowAlpha','highAlpha','lowBeta','highBeta','lowGamma','midGamma','Meditation','Attention']].to_numpy()
        #print('[TEST] self._X : ', self._X)
        if(isTrained is False):
            self._scaler = RobustScaler()
            self._scaler.fit(self._X)
        self._X = self._scaler.transform(self._X)
        self._xhat = arguList[0:1]
        #print(arguList[0:1])
        self._yhat = self._model.predict_classes(self._xhat,verbose=0)
        #print(self._yhat)

        if self._yhat[0] == 1 :
            print("emergency call")
            sys.exit(-1)
        else:
            print("normal")
            #print(self._yhat)

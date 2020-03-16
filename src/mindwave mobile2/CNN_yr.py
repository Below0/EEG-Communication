import random
import pandas as pd, numpy as np
from numpy import *
from sklearn.preprocessing import RobustScaler
from keras.utils import np_utils
from keras.models import Sequential
from keras.callbacks import EarlyStopping
from keras.layers import Dense, Dropout, Activation, Flatten, Conv1D, pooling
from keras.layers.convolutional import Convolution1D, MaxPooling1D

class ConvoultionalNeuralNetwork:

    def __init__(self):
        self._normal = None
        self._emerge = None
        self._X = None
        self._Y = None
        self._bclass = None
        self._trainSize = None
        self._X_train = self._X_test = None
        self._Y_train = self._Y_test = None
        np.random.seed(30)

    def _readDataFromFile(self,normalFile,emergencyFile):
        self._normal=pd.read_csv(normalFile,header=None) # 일반 파일 읽어오기
        self._emerge=pd.read_csv(emergencyFile,header=None) # 상황 파일 읽어오기

        del self._normal[0] # index column 제거
        del self._emerge[0] # "

        self._normal['label'] = 'safe'
        self._emerge['label'] = 'unsafe'

        # Convolution을 위한 2개의 데이터 모음을 하나로 모으기
        self._X = pd.concat([self._normal,self._emerge],ignore_index = True)
        self._X = self._X.drop([self._X.index[0]]) # header 삭제
        self._trainSize = int(70*((self._X.shape[0])/100)) # training size : header 제외

        # binary classification
        self._bclass = {'safe':[1,0],'unsafe':[0,1]}

        # Y를 비어있는 np array(모든 원소가 2개짜리 리스트로 되어있는)로 만들기
        self._Y = np.empty((self._x.shape[0],2)) # header 제외

        # enumerate : tuple형태로 (index,value)값 리턴
        for i, v in enumerate(self._X['label']):
            self._Y[i] = self._bclass[v] # i번째 인덱스에 v값에 맞는 value 입력

        #X축의 label을 제외한 테스트 데이터 셋
        del self._X['label']
        self._X = self._X.to_numpy() # list to numpy

        # temp에 x,y값을 한 덩어리로 묶어 리스트 형태로 저장
        tmp = [[x_tmp,y_tmp] for x_tmp,y_tmp in zip(self._X,self._Y)]
        random.shuffle(tmp) # 섞기
        self._X = [n[0] for n in tmp] # 섞은 데이터를 다시 X에 저장
        self._Y = [n[1] for n in tmp] # 섞은 데이터를 다시 Y에 저장

        # float32형으로 np array로 만들기
        self._X = np.asarray(self._X,dtype=np.float32)
        self._Y = np.asarray(self._Y,dtype=np.float32)

        # training set : 70% , testing set : 30%
        self._X_train,self._Y_train = self._X[1:self_trainSize],self._Y[1:self._trainSize]
        self._X_test,self._Y_test = self._X[self._trainSize:],self._Y[self._trainSize:]

        x_train = x_train.reshape(x_train.shape[0],10,1)
        x_test = x_test.reshape(x_test.shape[0],10,1)

        print('x_train shape:', x_train.shape[1])
        print(x_train.shape[0], 'train samples')
        print(x_test.shape[0], 'test samples')
        print(y_train.shape[1])

    def evaluate_model(x_train, y_train, x_test, y_test):
        model = Sequential()
        verbose, epochs, batch_size = 0, 10, 32
        n_timesteps, n_features, n_outputs = x_train.shape[1], x_train.shape[2], y_train.shape[1]
        model.add(Convolution1D(filters=64, kernel_size=3, activation='relu',
                        input_shape=(n_timesteps,n_features)))
        model.add(Convolution1D(filters=64, kernel_size = 3, activation='relu'))
        model.add(Dropout(0.25))
        model.add(MaxPooling1D(pool_size = 2))
        model.add(Flatten())
        model.add(Dense(100, activation='relu'))
        model.add(Dropout(0.5))
        model.add(Dense(n_outputs, activation='softmax'))

        model.compile(loss='categorical_crossentropy',optimizer='adam',metrics=['accuracy'])
        hist=model.fit(x_train, y_train, epochs=epochs, batch_size=batch_size, verbose=verbose)
        print(hist.history['loss'])

        _, accuracy= model.evaluate(x_test, y_test, batch_size=batch_size, verbose=0)
        return accuracy

    repeats=10
    scores = list()
    for r in range(repeats):
	score = evaluate_model(x_train, y_train, x_test, y_test)
	score = score * 100.0
	print('>#%d: %.3f' % (r+1, score))
	scores.append(score)
    # summarize results
    print(scores)
    m, s = mean(scores), std(scores)
    print('Accuracy: %.3f%% (+/-%.3f)' % (m, s))

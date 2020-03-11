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

    def __init__(self,normalFile,emergFile):
        np.random.seed(30)

    def _readDataFromFile(self,normalFile,currentFile):
    self._test1=pd.read_csv('normal.csv',header=None)
    self._test2=pd.read_csv('emergency.csv',header=None)

    self._test1.drop(test1.columns[[0]], axis='columns')
    self._test2.drop(test1.columns[[0]], axis='columns')

    self._test1["label"] = "unsafe"
    self._test2["label"] = "safe"

    self._X=pd.concat([test1, test2])

    #Y를 범주형 데이터로 전환(우리가 쓰는 데이터)
    self._bclass = {'safe':[1, 0], 'unsafe':[0, 1]}
    self._y = np.empty((1123, 2))
    for i, v in enumerate(X['label']):
        self._y[i] = self._bclass[v]

    #X축의 label을 제외한 테스트 데이터 셋
    del X['label']
    X=X.to_numpy()
    X.shape

    tmp = [[x,y_tmp] for x, y_tmp in zip(X, y)]
    random.shuffle(tmp)
    X= [n[0] for n in tmp]
    y = [n[1] for n in tmp]

    X = np.asarray(X, dtype=np.float32)
    y = np.asarray(y, dtype=np.float32)

    x_train, y_train = X[1:900], y[1:900]
    x_test, y_test = X[900:], y[900:]

    x_train = x_train.reshape(x_train.shape[0], 10, 1)
    x_test = x_test.reshape(x_test.shape[0], 10, 1)

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

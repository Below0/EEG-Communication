#!/usr/bin/env python
# coding: utf-8

# In[15]:


from keras.models import Sequential
from keras.utils import np_utils
from keras.layers import Dense, Dropout, Activation, Flatten, Conv1D, pooling
from keras.layers.convolutional import Convolution1D, MaxPooling1D
from keras.callbacks import EarlyStopping
import pandas as pd, numpy as np
from sklearn.preprocessing import RobustScaler
import random
from numpy import *

np.random.seed(30)

test1=pd.read_csv('test_normal.csv', header=None)
test2=pd.read_csv('test_scared.csv', header=None)

#test1=pd.read_csv('normal4.csv')
#test2=pd.read_csv('emer4.csv')

#test1 = test1.drop(["Time", "Unnamed: 0"], axis=1)
#test2 = test2.drop(["Time", "Unnamed: 0"], axis=1)
test1.drop(test1.columns[[0]], axis='columns')
test2.drop(test1.columns[[0]], axis='columns')


#test1.head()
#test2.head()


# In[21]:


test1["label"] = "safe"
test2["label"] = "unsafe"

X=pd.concat([test1, test2])

#print(X.shape)
#print(X)
#"""
#Y를 범주형 데이터로 전환
bclass = {'safe':[1, 0], 'unsafe':[0, 1]}
y = np.empty((, 2))
for i, v in enumerate(X['label']):
    y[i] = bclass[v]

#X축의 label을 제외한 테스트 데이터 셋
del X['label']
#X = X[['delta','theta','lowAlpha','highAlpha','lowBeta','highBeta','lowGamma','midGamma']].to_numpy()
X=X.to_numpy()
X.shape
#"""


# In[22]:


tmp = [[x,y_tmp] for x, y_tmp in zip(X, y)]
random.shuffle(tmp)
X= [n[0] for n in tmp]
y = [n[1] for n in tmp]

X = np.asarray(X, dtype=np.float32)
y = np.asarray(y, dtype=np.float32)

#print(X.shape, y.shape)


# In[24]:


#scaler = RobustScaler()
#scaler.fit(X)
#X = scaler.transform(X)
#print(X)
#np.mean(X), np.std(X)


# In[25]:


x_train, y_train = X[1:900], y[1:900]
x_test, y_test = X[900:], y[900:]


# In[26]:


x_train = x_train.reshape(x_train.shape[0], 10, 1)
x_test = x_test.reshape(x_test.shape[0], 10, 1)

print('x_train shape:', x_train.shape[1])
print(x_train.shape[0], 'train samples')
print(x_test.shape[0], 'test samples')
print(y_train.shape[1])


# In[27]:


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


# In[28]:


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


# In[ ]:

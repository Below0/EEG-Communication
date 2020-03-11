#!/usr/bin/env python
# coding: utf-8

# In[24]:


from keras.models import Sequential
from keras.utils import np_utils
from keras.layers.core import Dense, Dropout, Activation
from keras.callbacks import EarlyStopping
import pandas as pd, numpy as np
from sklearn.preprocessing import RobustScaler
import random


#test1=pd.read_csv('Result_per_second.csv')
#test2=pd.read_csv('Result_game.csv')
test1=pd.read_csv('normal4.csv', header=None)
test2=pd.read_csv('emer4.csv', header=None)

#test1 = test1.drop(["Time", "Unnamed: 0"], axis=1)
#test2 = test2.drop(["Time", "Unnamed: 0"], axis=1)


#test1.head()
#print(test2.shape)


# In[8]:


test1["label"] = "unsafe"
test2["label"] = "safe"

csv=pd.concat([test1, test2])

bclass = {'safe':[1, 0], 'unsafe':[0, 1]}
y = np.empty((1123, 2))
for i, v in enumerate(csv['label']):
    y[i] = bclass[v]

del csv['label']
#X = csv[['delta','theta','lowAlpha','highAlpha','lowBeta','highBeta','lowGamma','midGamma','Meditation','Attention']].to_numpy()
X=csv.to_numpy()

#scaler = RobustScaler()
#scaler.fit(X)
#X = scaler.transform(X)
#print(X_rob)
#np.mean(X_rob), np.std(X_rob)

tmp = [[x,y_tmp] for x, y_tmp in zip(X, y)]
random.shuffle(tmp)
X= [n[0] for n in tmp]
y = [n[1] for n in tmp]

X = np.asarray(X, dtype=np.float32)
y = np.asarray(y, dtype=np.float32)


# In[9]:


x_train, y_train = X[1:900], y[1:900]
x_test, y_test = X[900:], y[900:]

print(x_train.shape, y_train.shape, x_test.shape, y_test.shape)


# In[10]:


model = Sequential()
"""
model.add(Convolution2D(32, 3, 3,
                        border_mode='same',
                        input_shape=X_train.shape[1:]))
                        """
model.add(Dense(512, input_shape=(10,)))
model.add(Activation('relu'))
model.add(Dropout(0.1))

model.add(Dense(512))
model.add(Activation('relu'))
model.add(Dropout(0.1))

model.add(Dense(2))
model.add(Activation('softmax'))

model.compile(
    loss='binary_crossentropy',
    optimizer='rmsprop',
    metrics=['accuracy']
)


# In[11]:


#모델 학습시키기
hist = model.fit(x_train, y_train, epochs=50, 
                 batch_size=32, validation_data=(x_test, y_test))


# In[13]:


print("LOSS")
print(hist.history['loss'])
#print(hist.history['acc'])

loss_and_metrics = model.evaluate(x_test, y_test, batch_size=32)
print('LOSS_AND_METRICS')
print(loss_and_metrics)

xhat = x_test[0:1]
print('XHAT')
print(xhat)
print(y_test[0:1])
yhat = model.predict(xhat)
print('YHAT')
print(yhat)


dat=pd.read_csv('emer_test.csv')
print(dat)
dat.drop(['Unnamed: 0'],axis=1,inplace=True)
print(dat)
X = dat[['delta','theta','lowAlpha','highAlpha','lowBeta','highBeta','lowGamma','midGamma','Meditation','Attention']].to_numpy()
xhat = dat[0:1]
print('XHAT')
print(xhat)
yhat = model.predict(xhat)
print('YHAT')
print(yhat)

#!/usr/bin/env python
# coding: utf-8

# In[1]:


from keras.models import Sequential
from keras.utils import np_utils
from keras.layers.core import Dense, Dropout, Activation
from keras.callbacks import EarlyStopping
import pandas as pd, numpy as np
from sklearn.preprocessing import RobustScaler
import random


test1=pd.read_csv('Result_per_second.csv')
test2=pd.read_csv('Result_game.csv')


# In[8]:


test1["label"] = "unsafe"
test2["label"] = "safe"

csv=pd.concat([test1, test2])
##test_size 지정(70% : train size, 30: test size)
test_size = int(70*(csv.shape[0]/100))

bclass = {'safe':[1, 0], 'unsafe':[0, 1]}
y = np.empty((csv.shape[0], 2))
for i, v in enumerate(csv['label']):
    y[i] = bclass[v]

del csv['label']
X = csv[['delta','theta','lowAlpha','highAlpha','lowBeta','highBeta','lowGamma','midGamma','Meditation','Attention']].to_numpy()
#X=csv.to_numpy()

scaler = RobustScaler()
scaler.fit(X)
X = scaler.transform(X)

tmp = [[x,y_tmp] for x, y_tmp in zip(X, y)]
random.shuffle(tmp)
X= [n[0] for n in tmp]
y = [n[1] for n in tmp]

X = np.asarray(X, dtype=np.float32)
y = np.asarray(y, dtype=np.float32)
#print(y)


# In[3]:


x_train, y_train = X[1:test_size], y[1:test_size]
x_test, y_test = X[test_size:], y[test_size:]

#print(x_train.shape, y_train.shape, x_test.shape, y_test.shape)


# In[4]:


model = Sequential()
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


# In[9]:


#모델 학습시키기
hist = model.fit(x_train, y_train, epochs=50, 
                 batch_size=32, validation_data=(x_test, y_test))


# In[10]:


model_json = model.to_json()
with open("model.json", "w") as json_file : 
    json_file.write(model_json)
model.save_weights("model.h5")
print("Saved model to disk")


# In[31]:


dat=pd.read_csv('Result_normal.csv')
del dat['Unnamed: 0']
del dat['Time']

X = dat[['delta','theta','lowAlpha','highAlpha','lowBeta','highBeta','lowGamma','midGamma','Meditation','Attention']].to_numpy()

test_scaler = RobustScaler()
test_scaler.fit(X)
X = test_scaler.transform(X)

xhat = X[0:1]

yhat = model.predict(xhat)

if yhat[0][0] == 1 :
    print("emergency call")
else:
    print("normal")


# In[ ]:





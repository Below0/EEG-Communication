import random
import pandas as pd, numpy as np
from keras.utils import np_utils
from keras.models import Sequential
from keras.callbacks import EarlyStopping
from sklearn.preprocessing import RobustScaler
from keras.layers.core import Dense, Dropout, Activation

test1=pd.read_csv('Result_per_second.csv')
test2=pd.read_csv('Result_game.csv')

test1 = test1.drop(["Time", "Unnamed: 0"], axis=1)
test2 = test2.drop(["Time", "Unnamed: 0"], axis=1)

test1["label"] = "unsafe"
test2["label"] = "safe"

csv=pd.concat([test1, test2])

test_size = int(70*(csv.shape[0]/100))

bclass = {'safe':[1, 0], 'unsafe':[0, 1]}
y = np.empty((csv.shape[0], 2))
for i, v in enumerate(csv['label']):
    y[i] = bclass[v]

del csv['label']
X = csv[['delta','theta','lowAlpha','highAlpha','lowBeta','highBeta','lowGamma','midGamma','Meditation','Attention']].to_numpy()

scaler = RobustScaler()
scaler.fit(X)
X = scaler.transform(X)

tmp = [[x,y_tmp] for x, y_tmp in zip(X, y)]
random.shuffle(tmp)
X= [n[0] for n in tmp]
y = [n[1] for n in tmp]

X = np.asarray(X, dtype=np.float32)
y = np.asarray(y, dtype=np.float32)

x_train, y_train = X[1:test_size], y[1:test_size]
x_test, y_test = X[test_size:], y[test_size:]

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

#모델 학습시키기
hist = model.fit(x_train, y_train, epochs=50,batch_size=32, validation_data=(x_test, y_test))

dat=pd.read_csv('emer_test.csv')
dat.drop(['Unnamed: 0'], axis=1, inplace=True)
X = dat[['delta','theta','lowAlpha','highAlpha','lowBeta','highBeta','lowGamma','midGamma','Meditation','Attention']].to_numpy()
xhat = dat[0:1]
yhat = model.predict(xhat)
if yhat[0][0] == 1 :
    print("emergency call")
else:
    print("normal")

import keras
from keras.models import Sequential
from keras.layers import Dense, Dropout, Activation
from keras.optimizers import SGD
from keras.layers.normalization import BatchNormalization
from keras import regularizers
import matplotlib.pyplot as plt
import json
import random

# Generate dummy data
import numpy as np
with open('datas.json','r') as f:
    datas=json.load(f)
x_train=[]
y_train=[]
for data in datas:
    vector=np.fromstring(data[0],sep=',')
    x_train.append(vector)
    y_train.append(data[1])

# shuffle data
dt = list(zip(x_train, y_train))
random.shuffle(dt)
x_train, y_train = zip(*dt)

x_train=np.array(x_train)*1000 # scale up
y_train=np.array(y_train)
#print(x_train.shape)
#print(y_train.shape)
y_train = keras.utils.to_categorical(y_train, num_classes=5)
#print(y_train.shape)
#x_test = np.random.random((100, 20))
#y_test = keras.utils.to_categorical(np.random.randint(10, size=(100, 1)), num_classes=10)

model = Sequential()
# Dense(64) is a fully-connected layer with 64 hidden units.
# in the first layer, you must specify the expected input data shape:
# here, 20-dimensional vectors.

reg=0.7
dropout=0.5
model.add(Dense(256, activation='relu', input_dim=300,kernel_regularizer=regularizers.l2(reg)))
model.add(BatchNormalization())
model.add(Dropout(dropout))
model.add(Dense(128, activation='relu',kernel_regularizer=regularizers.l2(reg)))
model.add(BatchNormalization())
model.add(Dropout(dropout))
#model.add(Dense(64, activation='relu',kernel_regularizer=regularizers.l2(reg)))
#model.add(BatchNormalization())
#model.add(Dropout(dropout))
model.add(Dense(5, activation='softmax'))

#sgd = SGD(lr=0.01, decay=1e-6, momentum=0.9, nesterov=True)
model.compile(loss='categorical_crossentropy',
              optimizer='rmsprop',
              metrics=['accuracy'])

hist=model.fit(x_train, y_train,
          epochs=100,
          batch_size=32,
          validation_split=0.3)
#print(hist.history)
#score = model.evaluate(x_test, y_test, batch_size=128)
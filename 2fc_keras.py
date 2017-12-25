import keras
from keras.models import Sequential
from keras.layers import Dense, Dropout, Activation
from keras.optimizers import SGD
from keras.layers.normalization import BatchNormalization
from keras import regularizers
import matplotlib.pyplot as plt
from ioutils import *


model = Sequential()

reg=0.5
dropout=0.5
model.add(Dense(256, activation='relu', input_dim=300,kernel_regularizer=regularizers.l2(reg)))
model.add(BatchNormalization())
model.add(Dropout(dropout))
model.add(Dense(128, activation='relu',kernel_regularizer=regularizers.l2(reg)))
model.add(BatchNormalization())
model.add(Dropout(dropout))
model.add(Dense(5, activation='softmax'))

num_epochs=150

intervals=[15,30,45,60,90]
for interval in intervals:
    filename='datasets/datas_'+str(interval)+'d.json'
    x_train,y_train=get_training_data_json(filename)
    x_train, y_train = shuffle_data(x_train,y_train)
    x_train=np.array(x_train)*1000 # scale up to avoid decimal computation loss
    y_train=np.array(y_train)
    y_train = keras.utils.to_categorical(y_train, num_classes=5)
    
    model.compile(loss='categorical_crossentropy',
              optimizer='rmsprop',
              metrics=['accuracy'])
    hist=model.fit(x_train, y_train,
          epochs=num_epochs,
          batch_size=32,
          validation_split=0.3)
    plt.plot(range(num_epochs),hist.history['val_acc'],range(num_epochs),hist.history['acc'])
    plt.savefig('figs/2fc_training_'+str(interval)+'days')
    plt.close()
#score = model.evaluate(x_test, y_test, batch_size=128)
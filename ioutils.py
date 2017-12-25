import numpy as np
import json
import random

def get_training_data_json(filename):
    """
    return x_train,y_train from json files
    containing list of datum.
    Each datum is a tuple, first item is a string of the imput array
    parse out the ','. The second item is a int indicating the class.
    """
    with open(filename,'r') as f:
        datas=json.load(f)
    x_train=[]
    y_train=[]
    for data in datas:
        vector=np.fromstring(data[0],sep=',')
        x_train.append(vector)
        y_train.append(data[1])
    return x_train,y_train

def shuffle_data(x_train,y_train):
    """
    pair up x,y and shuffle
    return the shuffled x,y
    """
    dt = list(zip(x_train, y_train))
    random.shuffle(dt)
    return zip(*dt)
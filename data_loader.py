import numpy as np
import pandas as pd
import random

def get_training_data(folder_name):
    df=pd.read_csv(folder_name+'X_cont.csv', sep=',')
    X_cont = df.values
    df=pd.read_csv(folder_name+'X_disc.csv', sep=',')
    X_disc = df.values
    df=pd.read_csv(folder_name+'Y.csv', sep=',')
    Y=df.values
    return X_cont,X_disc,Y

def shuffle_data(X_cont,X_disc,Y):
    """
    pair up x,y and shuffle
    return the shuffled x,y
    """
    perm=np.random.permutation(len(X_cont))
    return X_cont[perm],X_disc[perm],Y[perm]
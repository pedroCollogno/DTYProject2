from keras.models import Sequential
from keras.layers import LSTM, Dense
from keras.datasets import mnist
from keras.utils import np_utils
from keras.callbacks import TensorBoard
from keras import initializers
import utils as utils
import numpy as np
import pandas as pd
from time import time
import sys

"""This part runs if you run 'python model.py file_name' in the console
    :param 1: name of file in /pkl folder
"""
if __name__ == '__main__':
    df = pd.read_pickle('./pkl/{}.pkl'.format(sys.argv[1]))

    X = np.array(list(df['X'].values))
    Y = np.array(df['Y'].values)
    print(type(X), X.shape)
    print(type(Y), Y.shape)

    model = Sequential()
    model.add(LSTM(units = 32, input_shape=(None , 2)))
    model.add(Dense(1))

    model.compile(loss='mse', optimizer='rmsprop', metrics=['accuracy'])

    tensorboard = TensorBoard(log_dir="logs/{}".format(time()))

    model.fit(
        X,
        Y,
        batch_size=10,
        epochs=64,
        validation_split=0.05,
        callbacks=[tensorboard])


from keras.models import Sequential
from keras.layers import LSTM, Dense, Dropout, Embedding
from keras.datasets import mnist
from keras.utils import np_utils
from keras.callbacks import TensorBoard
from keras import initializers
from keras.optimizers import Adam
from keras import losses
from keras import backend
import utils as utils
import numpy as np
import pandas as pd
from time import time
import sys
import os
from progressbar import ProgressBar
import metrics 

def create_weighted_binary_crossentropy(zero_weight, one_weight):

    def weighted_binary_crossentropy(y_true, y_pred):

        # Original binary crossentropy (see losses.py):
        # K.mean(K.binary_crossentropy(y_true, y_pred), axis=-1)

        # Calculate the binary crossentropy
        b_ce = losses.binary_crossentropy(y_true, y_pred)

        # Apply the weights
        weight_vector = y_true * one_weight + (1. - y_true) * zero_weight
        weighted_b_ce = weight_vector * b_ce

        # Return the mean error
        return backend.mean(weighted_b_ce)

    return weighted_binary_crossentropy

"""This part runs if you run 'python model.py file_name' in the console
    :param 1: name of file in /pkl folder
"""
if __name__ == '__main__':
    file_path = './pkl/{}'.format(sys.argv[1])
    filelist = [ f for f in os.listdir(file_path)]
    df = pd.DataFrame(columns=['X', 'Y'])

    progress = 0
    pbar = ProgressBar(maxval=(len(filelist)))
    pbar.start()

    print("Getting the files...")
    for f in filelist:
        df_temp = pd.read_pickle('./pkl/{0}/{1}'.format(sys.argv[1], f))
        df = pd.concat([df,df_temp], ignore_index=True)
        df_temp = None
        progress += 1
        pbar.update(progress)


    pbar.finish()

    #df = pd.read_pickle('./pkl/{}.pkl'.format(sys.argv[1]))


    X = np.array(list(df['X'].values))
    Y = np.array(list(df['Y'].values))
    print(df.groupby('Y').count())
    print(type(X[0]))
    print(type(X), X.shape)
    print(type(Y), Y.shape)

    model = Sequential()
    model.add(LSTM(units = 64, input_shape=(None , 2)))
    model.add(Dense(1, activation="sigmoid"))

    # model.add(LSTM(output_dim=32,input_shape=(None , 2), activation='sigmoid', inner_activation='hard_sigmoid', return_sequences=True))
    # model.add(Dropout(0.5))
    # model.add(LSTM(output_dim=32, activation='sigmoid', inner_activation='hard_sigmoid'))
    # model.add(Dropout(0.5))
    # model.add(Dense(1, activation='sigmoid'))



    model.compile(loss='binary_crossentropy', optimizer='rmsprop', metrics=['accuracy', metrics.f1_score_threshold(), metrics.precision_threshold(), metrics.recall_threshold()])
    #Adam(lr=0.0005)
    tensorboard = TensorBoard(log_dir="logs/{}".format(time()))

    model.summary()

    model.fit(
        X,
        Y,
        batch_size=256,
        epochs=10,
        validation_split=0.33,
        callbacks=[tensorboard],
        shuffle=True)


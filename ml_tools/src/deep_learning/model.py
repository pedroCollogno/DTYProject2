from keras.models import Sequential, load_model
from keras.layers import LSTM, Dense, Dropout, Embedding
from keras.callbacks import TensorBoard, Callback, EarlyStopping
from keras.optimizers import Adam, RMSprop, Adadelta
from keras.layers import Bidirectional

import sklearn.metrics as skmetrics
from sklearn.cluster import DBSCAN
import matplotlib.pyplot as plt

from progressbar import ProgressBar
from time import time

import sys
import os
import random
import itertools

import numpy as np
import pandas as pd
import networkx as nx

if __name__ == "__main__":
    # If launching this file as a file, enlarge the scope to see all of the src folder of ml_tools package
    file_dir = os.path.abspath(os.path.dirname(__file__))
    sys.path.append(os.path.abspath(
        os.path.dirname(file_dir)))

from .metrics import *
from ..utils import config
from ..utils.log import create_new_folder

import logging
logger = logging.getLogger('backend')

PKL_DIR = config['PATH']['pkl']
PKL2_DIR = config['PATH']['pkl2']
WEIGHTS_DIR = config['PATH']['weights']

create_new_folder('tensorboard', config['PATH']['logs'])
LOG_DIR = os.path.join(config['PATH']['logs'], 'tensorboard')
DATA_DIR = config['PATH']['data']


def random_product(*args, repeat=1):
    """
        Random selection from itertools.product(*args, **kwds)
    """
    pools = [tuple(pool) for pool in args] * repeat
    return tuple(random.choice(pool) for pool in pools)


def fake_data(sequence_size, all=True, n_samples=1000, equalize=False):
    """ Generates fake data

    :param sequence_size: the size of the sequence to generate
    :param all: (optional) Boolean, if we want to generate all the possible combinations samples (be careful, goes in 2**sequence_size)
    :param n_samples: (optional) Number of samples generated if all = False
    :param equalize: (optional) Boolean, if we want to create as many 0 label as 1 label
    """
    # If we want all the possible combinations of size sequence_size (be careful this goes in 2**sequence_size)
    if all:
        fakeX = [np.reshape(list(i), (2, sequence_size)).T.tolist()
                 for i in itertools.product([0, 1], repeat=sequence_size*2)]
        fakeY = [1]*len(fakeX)
        for i in range(len(fakeX)):
            for couple in fakeX[i]:
                if couple == [1, 1]:
                    fakeY[i] = 0
                    break
    # For too long sequence_sizes, we might want to only get n_samples
    else:
        fakeX = []
        items = [[0, 0], [0, 1], [1, 0], [1, 1]]
        for k in range(n_samples):
            fakeX.append([random.choices(items, weights=[50, 10, 10, 1])[0]
                          for i in range(sequence_size)])
        fakeY = [1]*len(fakeX)
        for i in range(len(fakeX)):
            for couple in fakeX[i]:
                if couple == [1, 1]:
                    fakeY[i] = 0
                    break
    # If we want to get as much 0s as 1s in the labels (in case there are too many 0s)
    if equalize:
        indices = [i for (i, x) in enumerate(fakeY) if x == 0]
        logger.info("How many 0s : %s" % len(indices))
        n_ones = fakeY.count(1)
        logger.info("How many 1s : %s" % n_ones)
        indices_to_delete = random.sample(indices, len(indices)-n_ones)
        logger.info("How many indices to delete: %s" % len(indices_to_delete))
        for index in sorted(indices_to_delete, reverse=True):
            del fakeX[index]
            del fakeY[index]
    logger.info("How manys 0s : %s" % fakeY.count(0))
    logger.info("How manys 1s : %s" % fakeY.count(1))
    return(fakeX, fakeY)


def train():
    """ 
        Trains a model on data produced with fake_data function. Saves weights to './weights' folder
    """

    # Training is done on sequence size 50
    data = fake_data(50, all=False, equalize=False)

    X = np.array(data[0])
    Y = np.array(data[1])

    # The model of our neural network
    model = Sequential()
    model.add(LSTM(units=128, input_shape=(None, 2)))
    model.add(Dense(1, activation="sigmoid"))

    callback_dir = os.path.join(LOG_DIR, time())
    my_callbacks = [EarlyStopping(monitor='auc_roc', patience=300, verbose=1, mode='max'),
                    TensorBoard(log_dir=callback_dir)]

    model.compile(loss='binary_crossentropy', optimizer='rmsprop', metrics=[
                  'accuracy', auc_roc, f1_score_threshold(), precision_threshold(), recall_threshold()])

    model.fit(
        X,
        Y,
        batch_size=50,
        epochs=100,
        validation_split=0.2,
        callbacks=my_callbacks,
        shuffle=True
    )

    # Use this to save the weights to be able to reload them while testing
    create_new_folder('weights', DATA_DIR)
    model.save_weights(os.path.join(WEIGHTS_DIR, 'my_model_weights.h5'))


def test(file_name):
    """
        Pass the data (processed by processData in processDL.py) into the model
        Each comparaison between two emittors gives a score, all the scores are stored in a .pkl file
        :param file_name: Name of the folder where the preprocessed data is stored (see processDL.py), in the /pkl folder
    """

    file_path = os.path.join(PKL_DIR, file_name)

    filelist = [f for f in os.listdir(file_path)]
    df = pd.DataFrame(columns=['X', 'Y', 'id_Couple'])

    progress = 0
    pbar = ProgressBar(maxval=(len(filelist)))
    pbar.start()

    # Get all the files from the folder (each dataframe stored as .pkl file can contain max. 2000 lines (see processDL.py))
    logger.info("Getting the files...")
    for f in filelist:
        df_temp = pd.read_pickle(os.path.join(file_path, f))
        df = pd.concat([df, df_temp], ignore_index=True)
        df_temp = None
        progress += 1
        pbar.update(progress)
    pbar.finish()

    X = np.array(list(df['X'].values))
    Y = np.array(list(df['Y'].values))
    id_Couple = (list(df['id_Couple'].values))


    model = Sequential()
    model.add(LSTM(units=128, input_shape=(None, 2)))
    model.add(Dense(1, activation="sigmoid"))
    model.compile(loss='binary_crossentropy', optimizer='rmsprop', metrics=[
                  'accuracy', f1_score_threshold(), precision_threshold(), recall_threshold()])

    # Loads the pretrained wieghts
    model.load_weights(os.path.join(WEIGHTS_DIR, 'my_model_weights.h5'))

    X_new = []
    Y_new = []
    progress2 = 0
    pbar2 = ProgressBar(maxval=len(X))
    pbar2.start()
    logger.info("Passing some data in the first network...")
    # For all couples 
    for itemindex in range(len(X)):
        X_test = X[itemindex]
        Y_test = Y[itemindex]
        Y_new.append(Y_test)

        # We feed the network with sequence size 50, so we need to 'cut' the whole sequence into several 50-long sequences
        number_steps = int(len(X_test)/50)
        to_predict = []
        for i in range(number_steps):
            to_predict.append(X_test[i*50:(i+1)*50])
        to_predict = np.array(to_predict)

        predictions = model.predict(to_predict)
        X_new.append(predictions)

        progress2 += 1
        pbar2.update(progress2)
    pbar2.finish()

    df = pd.DataFrame(
        {
            'X_new': X_new,
            'Y_new': Y_new,
            'id_Couple': id_Couple
        }, columns=['X_new', 'Y_new', 'id_Couple'])

    # Store the result data (as X_new), Y_new = Y and id_couple in /pkl2 folder
    name = '{}.pkl'.format(file_name)
    create_new_folder('pkl2', DATA_DIR)
    file_to_save_path = os.path.join(PKL2_DIR, name)

    df.to_pickle(file_to_save_path)
    X = []
    Y = []

    logger.debug(df)

def train2(file_name):
    """ 
        Uses the data output by the neural network (with test()) and creates the clusters of emittors
        :param file_name: Name of the data file from the /pkl2 folder to use 
        :return: A list of all the predictions and all the emittors ids
    """

    name = '{}.pkl'.format(file_name)
    file_path = os.path.join(PKL2_DIR, name)

    df = pd.read_pickle(file_path)

    # Get the data

    X = np.array(list(df['X_new'].values))
    Y = np.array(list(df['Y_new'].values))
    id_Couple = list(df['id_Couple'].values)

    # How many 0 or 1

    logger.info("How many 0s : %s" % np.count_nonzero(Y == 0))
    logger.info("How many 1s : %s" % np.count_nonzero(Y == 1))

    # If we want to use a DBSCAN

    id1 = [couple[0] for couple in id_Couple]
    id2 = [couple[1] for couple in id_Couple]

    distance = [np.divide(1, (X[i])).mean() for i in range(len(X))]
    df = pd.DataFrame(
        {
            'id1': id1,
            'id2': id2,
            'distance': distance
        }, columns=['id1', 'id2', 'distance']
    )

    # Convert the df in a matrix
    distance_matrix = pd.pivot_table(
        df, index='id1', columns='id2', values='distance')
    distance_matrix.fillna(0, inplace=True)

    # Add rows and columns to index, fill with 0 the diag
    index = distance_matrix.index.union(distance_matrix.columns)
    distance_matrix = distance_matrix.reindex(
        index=index, columns=index, fill_value=0)

    # Add the transposed to get the whole distance matrix
    distance_matrix = distance_matrix + distance_matrix.T
    logger.debug("Before normalization")
    logger.debug(distance_matrix)

    # Normalize the distance matrix
    xmax, xmin = max(distance_matrix.max()), min(distance_matrix.min())
    logger.debug("X-Max :")
    logger.debug(xmax)
    normalized_distance_matrix = (distance_matrix - xmin)/(xmax - xmin)
    logger.debug("After normalization")
    logger.debug(normalized_distance_matrix)

    np_data = np.array(normalized_distance_matrix)

    # Use DBSCAN to predict the clusters
    prediction = DBSCAN(eps=0.0000002, min_samples=1,
                        metric="precomputed").fit_predict(np_data)

    # If we want to use the tresholds method
    threshold = False
    if threshold:
        thresholdNumber = 10e10
        Y_predicted = []
        for i in range(len(X)):
            predict = 1
            #product = np.prod(X_new[i])
            mean = np.divide(1, np.square(X[i])).mean()
            if mean > thresholdNumber:
                predict = 0
            Y_predicted.append(predict)

    return(prediction, list(index))

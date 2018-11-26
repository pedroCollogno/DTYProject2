from keras.models import Sequential, load_model
from keras.layers import LSTM, Dense, Dropout, Embedding
from keras.callbacks import TensorBoard, Callback, EarlyStopping
from keras.optimizers import Adam

import sklearn.metrics as skmetrics
from sklearn.cluster import DBSCAN
import matplotlib.pyplot as plt

from progressbar import ProgressBar
from time import time

import sys
import os
import random
import metrics

import itertools
import numpy as np
import pandas as pd


import networkx as nx

if __name__ == "__main__":
    # If launching this file as a file, enlarge the scope to see all of the src folder of ml_tools package
    file_dir = os.path.abspath(os.path.dirname(__file__))
    sys.path.append(os.path.abspath(
        os.path.dirname(file_dir)))

from utils import config
from utils.log import create_new_folder, logger

PKL_DIR = config['PATH']['pkl']
PKL2_DIR = config['PATH']['pkl2']
WEIGHTS_DIR = config['PATH']['weights']
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
    :param all: (optional) TODO: COMPLETE DOCS 
    :param n_samples: (optional) TODO: COMPLETE DOCS 
    :param equalize: (optional) TODO: COMPLETE DOCS 
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
        logger.info(fakeX[0])
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
    data = fake_data(50, all=False, equalize=False)

    X = np.array(data[0])
    Y = np.array(data[1])

    model = Sequential()
    model.add(LSTM(units=128, input_shape=(None, 2)))
    #model.add(LSTM(units = 128, input_shape=(None , 2)))
    model.add(Dense(1, activation="sigmoid"))

    callback_dir = os.path.join(LOG_DIR, time())
    my_callbacks = [EarlyStopping(monitor='auc_roc', patience=300, verbose=1, mode='max'),
                    TensorBoard(log_dir=callback_dir)]

    model.compile(loss='binary_crossentropy', optimizer='rmsprop', metrics=[
                  'accuracy', metrics.auc_roc, metrics.f1_score_threshold(), metrics.precision_threshold(), metrics.recall_threshold()])

    model.summary()

    model.fit(
        X,
        Y,
        batch_size=16,
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
        Tests stuff
        TODO: COMPLETE DOCS 
    """

    file_path = os.path.join(PKL_DIR, file_name)

    if len(sys.argv) > 1:
        file_path = os.path.join(PKL_DIR, sys.argv[1])

    filelist = [f for f in os.listdir(file_path)]
    df = pd.DataFrame(columns=['X', 'Y', 'id_Couple'])

    progress = 0
    pbar = ProgressBar(maxval=(len(filelist)))
    pbar.start()

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
    logger.info(id_Couple)

    model = Sequential()
    model.add(LSTM(units=128, input_shape=(None, 2)))
    model.add(Dense(1, activation="sigmoid"))
    model.compile(loss='binary_crossentropy', optimizer='rmsprop', metrics=[
                  'accuracy', metrics.f1_score_threshold(), metrics.precision_threshold(), metrics.recall_threshold()])
    model.load_weights(os.path.join(WEIGHTS_DIR, 'my_model_weights.h5'))

    #ones_index = np.where(Y==1)[0]

    X_new = []
    Y_new = []
    progress2 = 0
    pbar2 = ProgressBar(maxval=len(X))
    pbar2.start()
    logger.info("Passing some data in the first network...")
    #random_indexs = random.sample(range(0, len(X)), 50)

    for itemindex in range(len(X)):
        X_test = X[itemindex]
        Y_test = Y[itemindex]
        Y_new.append(Y_test)

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

    name = '{}.pkl'.format(file_name)
    create_new_folder('pkl2', DATA_DIR)
    file_to_save_path = os.path.join(PKL2_DIR, name)

    df.to_pickle(file_to_save_path)
    X = []
    Y = []

    logger.info(df)

    # predictions = []
    # for item in to_predict:
    #     predictions.append(model.predict(item))
    # print(predictions, predictions.count(1))


def train2(file_name):
    """ 
        Trains a model on data from '.pkl2' folder
        TODO: COMPLETE DOCS 
    """

    name = '{}.pkl'.format(file_name)
    file_path = os.path.join(PKL2_DIR, name)

    df = pd.read_pickle(file_path)

    # model2 = Sequential()
    # model2.add(LSTM(units=128, input_shape=(None, 1)))
    # model2.add(Dense(1, activation="sigmoid"))

    # Get the data

    X = np.array(list(df['X_new'].values))
    Y = np.array(list(df['Y_new'].values))
    id_Couple = list(df['id_Couple'].values)

    # Optional : Balances the 0 and 1

    nb_ones = np.count_nonzero(Y == 1)
    zeros_index = np.where(Y == 0)[0]
    df = df.drop(df.index[zeros_index[nb_ones:]])

    df = df.sample(frac=1)

    X_new = np.array(list(df['X_new'].values))
    Y_new = np.array(list(df['Y_new'].values))

    # How many 0 or 1

    logger.info("How many 0s :", np.count_nonzero(Y == 0))
    logger.info("How many 1s :", np.count_nonzero(Y == 1))

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
    logger.info(len(distance))
    distance_matrix = distance_matrix.reindex(
        index=index, columns=index, fill_value=0)

    # Add the transposed to get the whole distance matrix
    distance_matrix = distance_matrix + distance_matrix.T
    logger.info("Before normalization", distance_matrix)

    # Normalize the distance matrix
    xmax, xmin = max(distance_matrix.max()), min(distance_matrix.min())
    logger.info("X-Max :", xmax)
    normalized_distance_matrix = (distance_matrix - xmin)/(xmax - xmin)
    logger.info("After normalization", normalized_distance_matrix)

    np_data = np.array(normalized_distance_matrix)
    # print(np_data)
    prediction = DBSCAN(eps=0.0000002, min_samples=1,
                        metric="precomputed").fit_predict(np_data)

    # If we want to use the tresholds method
    threshold = True
    if threshold:

        Y_predicted = []
        for i in range(len(X)):
            predict = 1
            #product = np.prod(X_new[i])
            mean = np.divide(1, np.square(X[i])).mean()
            if mean > 10e10:
                predict = 0
            Y_predicted.append(predict)

        createNetworks(Y, np.array(Y_predicted), id_Couple)

        plotCompareThresholds(X, Y)

    return(prediction, list(index))


def plotCompareThresholds(X, Y):
    thresholds = [10e3, 10e4, 5*10e4, 10e5, 5*10e5, 10e6, 2*10e6, 5*10e6, 6*10e6,
                  7*10e6, 8*10e6, 9*10e6, 10e7, 2*10e7, 5*10e7, 10e8, 10e9, 10e10, 10e30]
    precision0 = []
    precision1 = []
    recall0 = []
    recall1 = []
    fscore0 = []
    fscore1 = []
    for threshold in thresholds:
        test = []
        Y_predicted = []
        for i in range(len(X)):
            predict = 1
            #product = np.prod(X_new[i])
            mean = np.divide(1, np.square(X[i])).mean()
            if mean > threshold:
                predict = 0
            Y_predicted.append(predict)
            test.append(abs(predict - Y[i]))
        score = skmetrics.precision_recall_fscore_support(Y, Y_predicted)
        #print ("Precision '1' :", score[0][1]," Recall '1' :", score[1][1], " Fscore '1' :", score[2][1], " Number of samples '1' :", score[3][1])
        #print ("Precision '0' :", score[0][0]," Recall '0' :", score[1][0], " Fscore '0' :", score[2][0], " Number of samples '0' :", score[3][0])
        precision0.append(score[0][0])
        precision1.append(score[0][1])
        recall0.append(score[1][0])
        recall1.append(score[1][1])
        fscore0.append(score[2][0])
        fscore1.append(score[2][1])

    # Plot
    ax1 = plt.subplot(311)
    ax1.set_xscale('log')
    plt.plot(thresholds, precision0, 'r')
    plt.plot(thresholds, precision1, 'b')
    plt.ylabel('Threshold')
    plt.xlabel('Precision')
    ax2 = plt.subplot(312, sharex=ax1, sharey=ax1)
    plt.plot(thresholds, recall0, 'r')
    plt.plot(thresholds, recall1, 'b')
    plt.ylabel('Threshold')
    plt.xlabel('Recall')
    ax3 = plt.subplot(313, sharex=ax1, sharey=ax1)
    plt.plot(thresholds, fscore0, 'r')
    plt.plot(thresholds, fscore1, 'b')
    plt.ylabel('Threshold')
    plt.xlabel('Fscore')
    plt.legend()
    plt.show()


def createNetworks(Y, Y_predicted, id_Couple, allLinks=False):

    if allLinks:

        id1 = [couple[0] for couple in id_Couple]
        id2 = [couple[1] for couple in id_Couple]
        df = pd.DataFrame(
            {
                'id1': id1,
                'id2': id2,
                'link': Y_predicted
            }, columns=['id1', 'id2', 'link']
        )
        logger.info(df)

        fig, ax = plt.subplots()
        G = nx.from_pandas_edgelist(df, 'id1', 'id2', edge_attr='link')
        durations = [i['link'] for i in dict(G.edges).values()]

        pos = nx.spring_layout(G)

        color_names = ['r', 'b']
        colors = [color_names[i['link']] for i in dict(G.edges).values()]
        logger.info(colors)

        nx.draw_networkx_nodes(G, pos, ax=ax, labels=True)
        nx.draw_networkx_edges(G, pos, edge_color=colors, ax=ax)
        _ = nx.draw_networkx_labels(G, pos, ax=ax)

        plt.show()

    else:

        fig, axes = plt.subplots(nrows=1, ncols=2)
        ax = axes.flatten()

        # Draw the graph for predicted data

        links_id1_predicted = []
        links_id2_predicted = []
        ones_index_predicted = np.where(Y_predicted == 1)[0]
        for index in ones_index_predicted:
            links_id1_predicted.append(id_Couple[index][0])
            links_id2_predicted.append(id_Couple[index][1])
        df = pd.DataFrame(
            {
                'Id1': links_id1_predicted,
                'Id2': links_id2_predicted
            }, columns=['Id1', 'Id2'])

        df_predicted = pd.crosstab(df.Id1, df.Id2)
        idx_predicted = df_predicted.columns.union(df_predicted.index)
        df_predicted = df_predicted.reindex(
            index=idx_predicted, columns=idx_predicted, fill_value=0)

        G_predicted = nx.from_pandas_adjacency(df_predicted)
        pos_predicted = nx.spring_layout(G_predicted)

        nx.draw_networkx(
            G_predicted, ax=ax[0], pos=pos_predicted, with_labels=True)
        ax[0].set_axis_off()

        # Draw the graph for the true data

        links_id1_true = []
        links_id2_true = []
        ones_index_true = np.where(Y == 1)[0]
        for index in ones_index_true:
            links_id1_true.append(id_Couple[index][0])
            links_id2_true.append(id_Couple[index][1])
        df = pd.DataFrame(
            {
                'Id1': links_id1_true,
                'Id2': links_id2_true
            }, columns=['Id1', 'Id2'])

        df_true = pd.crosstab(df.Id1, df.Id2)
        idx_true = df_true.columns.union(df_true.index)
        df_true = df_true.reindex(
            index=idx_true, columns=idx_true, fill_value=0)

        G_true = nx.from_pandas_adjacency(df_true)
        pos_true = nx.spring_layout(G_true)

        nx.draw_networkx(G_true, ax=ax[1], pos=pos_true, with_labels=True)
        ax[1].set_axis_off()

        # Plot both

        plt.show()


"""This part runs if you run 'python model.py file_name' in the console
    :param 1: name of file in /pkl folder
"""
if __name__ == '__main__':
    train2(sys.argv[1])

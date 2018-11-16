from keras.models import Sequential
from keras.layers import LSTM, Dense, Dropout, Embedding
from keras.datasets import mnist
from keras.utils import np_utils
from keras.callbacks import TensorBoard, Callback, EarlyStopping
from keras import initializers
from keras.optimizers import Adam
from keras import losses
from keras import backend
from keras.models import load_model
import sklearn.metrics as skmetrics 
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from time import time
import sys
import os
from progressbar import ProgressBar
import metrics 
import random
import itertools

def random_product(*args, repeat=1):
    "Random selection from itertools.product(*args, **kwds)"
    pools = [tuple(pool) for pool in args] * repeat
    return tuple(random.choice(pool) for pool in pools)

def fakeData(sequence_size, all=True, n_samples=1000, equalize=False):
    # If we want all the possible combinations of size sequence_size (be careful this goes in 2**sequence_size)
    if all:
        fakeX = [np.reshape(list(i), (2, sequence_size)).T.tolist() for i in itertools.product([0, 1], repeat=sequence_size*2)]
        fakeY = [1]*len(fakeX)
        for i in range(len(fakeX)):
            for couple in fakeX[i]:
                if couple == [1,1]:
                    fakeY[i]=0
                    break
    # For too long sequence_sizes, we might want to only get n_samples
    else: 
        fakeX = []
        items=[[0,0],[0,1],[1,0],[1,1]]
        for k in range (n_samples):
            fakeX.append([random.choices(items, weights=[50,10,10,1])[0] for i in range(sequence_size)])
        print(fakeX[0])
        fakeY = [1]*len(fakeX)
        for i in range(len(fakeX)):
            for couple in fakeX[i]:
                if couple == [1,1]:
                    fakeY[i]=0
                    break
    # If we want to get as much 0s as 1s in the labels (in case there are too many 0s)
    if equalize:
        indices = [i for i, x in enumerate(fakeY) if x == 0]
        print("How many 0s :", len(indices))
        n_ones = fakeY.count(1)
        print("How many 1s :", n_ones)
        indices_to_delete = random.sample(indices, len(indices)-n_ones)
        print("How many indices to delete:", len(indices_to_delete))
        for index in sorted(indices_to_delete, reverse=True):
            del fakeX[index]
            del fakeY[index]
    print("How manys 0s :", fakeY.count(0), "\nHow manys 1s :", fakeY.count(1))
    return(fakeX, fakeY)
    

def train():
    data = fakeData(50,all=False,equalize=False)

    X = np.array(data[0])
    Y = np.array(data[1])

    model = Sequential()
    model.add(LSTM(units = 128, input_shape=(None , 2)))
    #model.add(LSTM(units = 128, input_shape=(None , 2)))
    model.add(Dense(1, activation="sigmoid"))

    my_callbacks = [EarlyStopping(monitor='auc_roc', patience=300, verbose=1, mode='max'), 
                    TensorBoard(log_dir="logs/{}".format(time()))]

    model.compile(loss='binary_crossentropy', optimizer='rmsprop', metrics=['accuracy', metrics.auc_roc, metrics.f1_score_threshold(), metrics.precision_threshold(), metrics.recall_threshold()])

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
    #model.save_weights('./weights/my_model_weights.h5')

def test():
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

    X = np.array(list(df['X'].values))
    Y = np.array(list(df['Y'].values))


    model = Sequential()
    model.add(LSTM(units = 128, input_shape=(None , 2)))
    model.add(Dense(1, activation="sigmoid"))
    model.compile(loss='binary_crossentropy', optimizer='rmsprop', metrics=['accuracy', metrics.f1_score_threshold(), metrics.precision_threshold(), metrics.recall_threshold()])
    model.load_weights('./weights/my_model_weights.h5')

    
    #ones_index = np.where(Y==1)[0]


    X_new = []
    Y_new =[]
    progress2 = 0
    pbar2 = ProgressBar(maxval=len(X))
    pbar2.start()
    print("Passing some data in the first network...")
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
            'X_new' : X_new,
            'Y_new' : Y_new
        }, columns = ['X_new', 'Y_new'])
    df.to_pickle('./pkl2/{}.pkl'.format(sys.argv[1]))
    X=[]
    Y=[]



    # predictions = []
    # for item in to_predict:
    #     predictions.append(model.predict(item))
    # print(predictions, predictions.count(1))

def train2():
    df = pd.read_pickle('./pkl2/{}.pkl'.format(sys.argv[1]))
    print(df.head())
    print(df['X_new'][0])

    model2 = Sequential()
    model2.add(LSTM(units = 128, input_shape=(None , 1)))
    model2.add(Dense(1, activation="sigmoid"))

    X = np.array(list(df['X_new'].values))
    Y = np.array(list(df['Y_new'].values))

    nb_ones = np.count_nonzero(Y == 1)
    zeros_index = np.where(Y==0)[0]
    df = df.drop(df.index[zeros_index[nb_ones:]])

    df = df.sample(frac=1)

    X_new = np.array(list(df['X_new'].values))
    Y_new = np.array(list(df['Y_new'].values))

    print(df)
    print("How many 0s :", np.count_nonzero(Y_new==0))
    print("How many 1s :", np.count_nonzero(Y_new==1))

    thresholds = [10e3, 10e4, 5*10e4, 10e5, 5*10e5, 10e6,2*10e6, 5*10e6, 6*10e6, 7*10e6, 8*10e6, 9*10e6, 10e7, 2*10e7, 5*10e7, 10e8, 10e9, 10e10, 10e30]
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
        print ("Precision '1' :", score[0][1]," Recall '1' :", score[1][1], " Fscore '1' :", score[2][1], " Number of samples '1' :", score[3][1])
        print ("Precision '0' :", score[0][0]," Recall '0' :", score[1][0], " Fscore '0' :", score[2][0], " Number of samples '0' :", score[3][0])
        precision0.append(score[0][0])
        precision1.append(score[0][1])
        recall0.append(score[1][0])
        recall1.append(score[1][1])
        fscore0.append(score[2][0])
        fscore1.append(score[2][1])
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
    #plt.plot(<X AXIS VALUES HERE>, <Y AXIS VALUES HERE>, 'line type', label='label here')
    plt.legend()
    plt.show()



    # model2.compile(loss='binary_crossentropy', optimizer=Adam(lr=0.001), metrics=['accuracy', metrics.auc_roc, metrics.f1_score_threshold(), metrics.precision_threshold(), metrics.recall_threshold()])

    # my_callbacks = [EarlyStopping(monitor='auc_roc', patience=300, verbose=1, mode='max'), 
    #             TensorBoard(log_dir="logs2/{}".format(time()))]

    # model2.fit(
    #     X_new,
    #     Y_new,
    #     batch_size=1,
    #     epochs=100,
    #     validation_split=0.2,
    #     callbacks=my_callbacks,
    #     shuffle=True
    #     )



"""This part runs if you run 'python model.py file_name' in the console
    :param 1: name of file in /pkl folder
"""
if __name__ == '__main__':
    train2()

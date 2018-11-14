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
import utils as utils
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
    data = fakeData(80,all=False,equalize=False)

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
    model.load_weights('my_model_weights.h5')

    
    ones_index = np.where(Y==1)[0]

    all_Y_true = []
    all_Y_predicted = []

    random_indexs = random.sample(range(0,len(X)), 50)
    for itemindex in ones_index:
        X_test = X[itemindex]
        Y_test = Y[itemindex]
        all_Y_true.append(Y_test)


        number_steps = int(len(X_test)/50)
        to_predict = []
        for i in range(number_steps):
            to_predict.append(X_test[i*50:(i+1)*50])
        to_predict = np.array(to_predict)


        predictions = model.predict(to_predict)

        Y_predicted = 1
        for prediction in predictions:
            if prediction[0] < 10e-05:
                Y_predicted = 0
        all_Y_predicted.append(Y_predicted)
        #print("Predicted ", Y_predicted, ", while truth is ", Y_test)


    precision_list = [abs(all_Y_true[i] - all_Y_predicted[i]) for i in range(len(all_Y_true))]
    precision = precision_list.count(0)/len(precision_list)
    print("Et la precision du q :", precision)


    # predictions = []
    # for item in to_predict:
    #     predictions.append(model.predict(item))
    # print(predictions, predictions.count(1))



"""This part runs if you run 'python model.py file_name' in the console
    :param 1: name of file in /pkl folder
"""
if __name__ == '__main__':
    train()
    

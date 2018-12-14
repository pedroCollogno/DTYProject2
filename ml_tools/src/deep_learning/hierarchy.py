from keras import Sequential
from keras.layers import LSTM, Dropout, Dense
import metrics
from keras.callbacks import TensorBoard, Callback, EarlyStopping
from time import time
import numpy as np
from fake_network_hierarchy import create_fake_sequences, fake_hierarchy_emission
import os
import sys
import tkinter as tk
from tkinter import filedialog
import random

if __name__ == "__main__":
    # If launching this file as a file, enlarge the scope to see all of the src folder of ml_tools package
    file_dir = os.path.abspath(os.path.dirname(__file__))
    sys.path.append(os.path.abspath(
        os.path.dirname(file_dir)))
from utils import config
from utils.loading import get_track_streams_from_prp
from processDL import process_data_clusters, create_clusters
WEIGHTS_DIR=config['PATH']['weights']



def train_hierarchy():
    """ Trains and saves the weights of the model on generated data
    """
    model=Sequential()
    model.add(Dense(128, activation="relu"))
    model.add(Dropout(0.5))
    model.add(Dense(11, activation="softmax"))
    my_callbacks = [
                    TensorBoard(log_dir="logs/{}".format(time()))]
    model.compile(loss='sparse_categorical_crossentropy', optimizer='rmsprop', metrics=[
                  'accuracy', metrics.f1_score_threshold(), metrics.precision_threshold(), metrics.recall_threshold()])

    data, labels=fake_hierarchy_emission(100, 200000)
    X=np.array(data)
    Y=np.array(labels)
    print(X.shape)

    model.fit(
            X,
            Y,
            batch_size=100,
            epochs=20,
            callbacks=my_callbacks,
            shuffle=True,
            validation_split=0.2
    )
    model.save_weights(WEIGHTS_DIR+'/my_hierarchy.h5')

def test_hierarchy():
    """
    Tests the model on a PRP file
    """
    model=Sequential()
    model.add(Dense(128, activation="relu", input_shape=(1,100)))
    model.add(Dense(11, activation="softmax"))
    model.compile(loss='sparse_categorical_crossentropy', optimizer='rmsprop', metrics=[
                  'accuracy', metrics.f1_score_threshold(), metrics.precision_threshold(), metrics.recall_threshold()])
    model.load_weights(WEIGHTS_DIR+'/my_hierarchy.h5')
    root = tk.Tk()
    root.withdraw()
    file_path = filedialog.askopenfilename()
    root.update()
    track_streams = get_track_streams_from_prp(file_path)

    emitter_infos= process_data_clusters(track_streams)
    to_predict=[]
    total=0
    clusters=create_clusters(emitter_infos)
    dicto={}

    for k in emitter_infos:
        #print("emitter %s in cluster %s" %(k, emitter_infos[k]['network']))
        number_of_steps=len(emitter_infos[k]['steps'])//100
        total=0
        for i in range(number_of_steps):
            prediction=model.predict(np.array(([[emitter_infos[k]['steps'][100*i:100*(i+1)]]])))
            most_likely=prediction.argmax()
            #print(emitter_infos[k]['steps'][100*i:100*(i+1)])
            #print(prediction)
            total+=most_likely
        try:
            dicto[emitter_infos[k]['network']].append(total)
        except Exception:
            dicto[emitter_infos[k]['network']]=[]
            dicto[emitter_infos[k]['network']].append(total)
    print(dicto)

if __name__=="__main__":
    test_hierarchy()
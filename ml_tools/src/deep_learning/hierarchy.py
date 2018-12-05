from keras import Sequential
from keras.layers import LSTM, Dropout, Dense
import metrics
from keras.callbacks import TensorBoard, Callback, EarlyStopping
from time import time
import numpy as np
from fake_terrorist_hierarchy import create_fake_sequences  
import os
import sys
import tkinter as tk
from tkinter import filedialog

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
    model.add(LSTM(units=128, input_shape=(None, 1)))
    model.add(Dropout(0.5))
    model.add(Dense(3, activation="softmax"))
    my_callbacks = [
                    TensorBoard(log_dir="logs/{}".format(time()))]
    model.compile(loss='sparse_categorical_crossentropy', optimizer='rmsprop', metrics=[
                  'accuracy', metrics.f1_score_threshold(), metrics.precision_threshold(), metrics.recall_threshold()])

    data, labels=create_fake_sequences(1000,70,20)
    X=np.array(data)
    Y=np.array(labels)
    print(X.shape)

    model.fit(
            X,
            Y,
            batch_size=1000,
            epochs=5,
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
    model.add(LSTM(units=128, input_shape=(None, 1)))
    model.add(Dense(3, activation="softmax"))
    model.compile(loss='sparse_categorical_crossentropy', optimizer='rmsprop', metrics=[
                  'accuracy', metrics.f1_score_threshold(), metrics.precision_threshold(), metrics.recall_threshold()])
    model.load_weights(WEIGHTS_DIR+'/my_hierarchy.h5')
    root = tk.Tk()
    root.withdraw()
    file_path = filedialog.askopenfilename()
    root.update()
    track_streams = get_track_streams_from_prp(file_path)
    emittor_infos= process_data_clusters(track_streams)
    to_predict=[]
    total=0
    clusters=create_clusters(emittor_infos)
    dicto={}
    for k in emittor_infos:
        print("emittor %s in cluster %s" %(k, emittor_infos[k]['network']))
        prediction=model.predict(np.array(([[[a] for a in emittor_infos[k]['steps']]])))
        most_likely=prediction.argmax()
        try:
            dicto[emittor_infos[k]['network']].append(most_likely)
        except Exception:
            dicto[emittor_infos[k]['network']]=[most_likely]
        print(prediction)
        print(most_likely)
        print(len(emittor_infos[k]['steps']))
        if emittor_infos[k]['network']==1:
            total+=(emittor_infos[k]['steps']).count(1)/len(emittor_infos[k]['steps'])
        if (most_likely==0):
            print("big chef")
            print((emittor_infos[k]['steps']).count(1)/len(emittor_infos[k]['steps']))
        elif (most_likely==1):
            print("small chef")
            print((emittor_infos[k]['steps']).count(1)/len(emittor_infos[k]['steps']))
        else:
            print("shit unit")
            print((emittor_infos[k]['steps']).count(1)/len(emittor_infos[k]['steps']))
    print(total)
    print(dicto)
    print(clusters[0])
#print(test_hierarchy())
print(test_hierarchy()) 
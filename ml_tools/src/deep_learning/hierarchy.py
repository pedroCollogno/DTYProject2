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
from processDL import process_data_clusters
WEIGHTS_DIR=config['PATH']['weights']



def train_hierarchy():
    model=Sequential()
    model.add(LSTM(units=128, input_shape=(1, 1000)))
    model.add(Dropout(0.5))
    model.add(Dense(3, activation="softmax"))
    my_callbacks = [
                    TensorBoard(log_dir="logs/{}".format(time()))]
    model.compile(loss='sparse_categorical_crossentropy', optimizer='rmsprop', metrics=[
                  'accuracy', metrics.f1_score_threshold(), metrics.precision_threshold(), metrics.recall_threshold()])

    data, labels=create_fake_sequences(10000,1000)
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
    model=Sequential()
    model.add(LSTM(units=128, input_shape=(1, 1000)))
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
    for k in emittor_infos:
        print("emittor %s in cluster %s" %(k, emittor_infos[k]['network']))
        prediction=model.predict(np.array(([[emittor_infos[k]['steps'][:1000]]])))
        most_likely=prediction.argmax()
        print(prediction)
        print(most_likely)
        if (most_likely==0):
            print("big chef")
        elif (most_likely==1):
            print("small chef")
            print((emittor_infos[k]['steps'][:1000]).count(1)/1000.0)
        else:
            print("shit unit")
            print((emittor_infos[k]['steps'][:1000]).count(1)/1000.0)
#print(test_hierarchy())
print(test_hierarchy()) 
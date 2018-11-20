from time import time
import metrics
from fake_data_clusters import multiple_fake_clusters
import numpy as np
from keras.models import Sequential, load_model
from keras.layers import LSTM, Dense, Dropout, Embedding
from keras.callbacks import TensorBoard, Callback, EarlyStopping
from keras.optimizers import Adam, RMSprop, Adadelta
from keras.layers import Bidirectional
import os
import sys
from sklearn.metrics import recall_score
from sklearn.metrics import precision_score

if __name__ == "__main__":
    # If launching this file as a file, enlarge the scope to see all of the src folder of ml_tools package
    file_dir = os.path.abspath(os.path.dirname(__file__))
    sys.path.append(os.path.abspath(
        os.path.dirname(file_dir)))

from processDL import create_clusters


def train():
    fake_data, fake_labels = multiple_fake_clusters(500, 50, 10, 10)
    X = np.array(fake_data)
    Y = np.array(fake_labels)

    model = Sequential()
    model.add(LSTM(units=128, input_shape=(2, 50)))
    model.add(Dense(1, activation="sigmoid"))

    my_callbacks = [EarlyStopping(monitor='auc_roc', patience=300, verbose=1, mode='max'),
                    TensorBoard(log_dir="logs/{}".format(time()))]

    model.compile(loss='binary_crossentropy', optimizer='rmsprop', metrics=[
                  'accuracy', metrics.auc_roc, metrics.f1_score_threshold(), metrics.precision_threshold(), metrics.recall_threshold()])
    model.fit(
        X,
        Y,
        batch_size=100,
        epochs=5,
        validation_split=0.2,
        callbacks=my_callbacks,
        shuffle=True
    )

    # Use this to save the weights to be able to reload them while testing
    model.save_weights('./weights/my_model_clusters_weights.h5')


def test():
    real_clusters, ei = create_clusters()
    labels = []
    real_data = []
    for cluster in real_clusters:
        for emittor in real_clusters[cluster]:
            step_nb = len(ei[emittor]['steps'])
            for cluster_secondary in real_clusters:
                cluster_secondary_cumulated = [0 for k in range(step_nb)]
                if cluster == cluster_secondary:
                    label = True
                else:
                    label = False
                for emittor_secondary in real_clusters[cluster_secondary]:
                    if emittor != emittor_secondary:
                        cluster_secondary_cumulated = [int(
                            cluster_secondary_cumulated[k] or ei[emittor_secondary]['steps'][k]) for k in range(step_nb)]
                if not (len(real_clusters[cluster])==1 and cluster_secondary==cluster):
                    for sequence_iterator in range(step_nb//50):
                        real_data.append([ei[emittor]['steps'][sequence_iterator*50:(sequence_iterator+1)*50],
                                            cluster_secondary_cumulated[sequence_iterator*50:(sequence_iterator+1)*50]])
                        labels.append(label)
                else:
                    print("1 emittor cluster comparing with itself")

    model = Sequential()
    model.add(LSTM(units=128, input_shape=(2, 50)))
    #model.add(Dense(2, activation='relu'))
    model.add(Dense(1, activation="sigmoid"))
    model.compile(loss='binary_crossentropy', optimizer='rmsprop', metrics=[
                  'accuracy', metrics.f1_score_threshold(), metrics.precision_threshold(), metrics.recall_threshold()])
    model.load_weights('./weights/my_model_clusters_weights.h5')

    to_predict=np.array(real_data)
    predictions=model.predict(to_predict)
    predictions=np.array([k[0] for k in predictions])
    labels=np.array(labels)
    print(len(labels))
    new_labels=[]
    new_predictions=[]
    for k in range(len(labels)/39):
        total_prediction=0
        isLabelTrue=labels[39*k]
        for i in range(39):
            total_prediction+=predictions[39*k+i]
            if not(isLabelTrue==(labels[39*k+i])):
                print('PROBLEM')
        new_labels.append(isLabelTrue)
        new_predictions.append(total_prediction)
    print(len(new_labels))
    print(len(new_predictions))
    print(recall_score(labels,predictions))
    print(recall_score(labels,predictions, pos_label=0))
    print(precision_score(labels,predictions))
    print(precision_score(labels,predictions, pos_label=0))
    print('reworked')
    print(recall_score(new_labels,new_predictions))
    print(recall_score(new_labels,new_predictions, pos_label=0))
    print(precision_score(labels,predictions))
    print(precision_score(labels,predictions, pos_label=0))
    

test()

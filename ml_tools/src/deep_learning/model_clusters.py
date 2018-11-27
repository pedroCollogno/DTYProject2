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
from sys import platform as sys_pf
import matplotlib
matplotlib.use("TkAgg")
from matplotlib import pyplot as plt
    


if __name__ == "__main__":
    # If launching this file as a file, enlarge the scope to see all of the src folder of ml_tools package
    file_dir = os.path.abspath(os.path.dirname(__file__))
    sys.path.append(os.path.abspath(
        os.path.dirname(file_dir)))

from processDL import create_clusters, create_emittor_comparison_with_cluster, create_cheat_comparison_with_cluster


def train():
    """
    Builds fake data to train the model on it.
    Saves the weights calculated for the following tests
    """
    fake_data, fake_labels = multiple_fake_clusters(500, 50, 10, 10)
    X = np.array(fake_data)
    Y = np.array(fake_labels)

    model = Sequential()
    model.add(LSTM(units=128, input_shape=(2, 50)))
    model.add(Dropout(0.5))
    model.add(Dense(1, activation="sigmoid"))

    my_callbacks = [EarlyStopping(monitor='auc_roc', patience=300, verbose=1, mode='max'),
                    TensorBoard(log_dir="logs/{}".format(time()))]

    model.compile(loss='binary_crossentropy', optimizer='rmsprop', metrics=[
                  'accuracy', metrics.auc_roc, metrics.f1_score_threshold(), metrics.precision_threshold(), metrics.recall_threshold()])
    model.fit(
        X,
        Y,
        batch_size=100,
        epochs=10,
        validation_split=0.2,
        callbacks=my_callbacks,
        shuffle=True
    )

    # Use this to save the weights to be able to reload them while testing
    model.save_weights('./weights/my_model_clusters_weights.h5')

def train_real():
    """
    We train the model on a certain situation stored in a PRP file,
    it creates clusters from the PRP file and compares every single emittor with every cluster
    We store the weights in a file to use them for testing
    """ 
    real_clusters, ei = create_clusters()
    real_data, labels, step_nb =create_cheat_comparison_with_cluster(real_clusters, ei)
    X = np.array(real_data)
    Y = np.array(labels)

    model = Sequential()
    model.add(LSTM(units=128, input_shape=(2, 50)))
    model.add(Dropout(0.5))
    model.add(Dense(1, activation="sigmoid"))

    my_callbacks = [EarlyStopping(monitor='auc_roc', patience=300, verbose=1, mode='max'),
                    TensorBoard(log_dir="logs/{}".format(time()))]

    model.compile(loss='binary_crossentropy', optimizer='rmsprop', metrics=[
                  'accuracy', metrics.auc_roc, metrics.f1_score_threshold(), metrics.precision_threshold(), metrics.recall_threshold()])
    model.fit(
        X,
        Y,
        batch_size=100,
        epochs=30,
        validation_split=0.4,
        callbacks=my_callbacks,
        shuffle=True
    )

    # Use this to save the weights to be able to reload them while testing
    model.save_weights('./weights/my_real_model_clusters_weights.h5')


def prediction_processing(predictions,labels, threshold, step_nb):
    """
    Labels the total prediction on all sequences according to threshold
    :param predictions: The predictions for every tuple (emittor, cluster, sequence)
    :param labels: The real labels of every tuple (emittor, cluster, sequence)
    :param threshold: The threshold defining from where we label as False
    :return: The scores (precision, recall) for both True and False
    """
    new_labels=[]
    new_predictions=[]
    number_sequences=step_nb//50
    for k in range(len(labels)//number_sequences):
        total_prediction=0
        isLabelTrue=labels[number_sequences*k]
        for i in range(number_sequences):
            total_prediction+=(1/predictions[number_sequences*k+i])
            if not(isLabelTrue==(labels[number_sequences*k+i])):
                print('problem')
        if total_prediction>threshold:
            total_prediction=False
        else:
            total_prediction=True
        new_labels.append(isLabelTrue)
        new_predictions.append(total_prediction)
    recall_1=recall_score(new_labels,new_predictions)
    recall_0=recall_score(new_labels,new_predictions, pos_label=0)
    precision_1=precision_score(new_labels,new_predictions)
    precision_0=precision_score(new_labels,new_predictions, pos_label=0)
    return((recall_1,recall_0,precision_1,precision_0), new_predictions, new_labels)

def test():

    """
    Tests our model on unseen data. We need first to pre-process the data
    Shows the recall, precision for different thresholds on a graph.
    We can choose the weights of the training on real data or on fake data generated
    """
    real_clusters, ei = create_clusters()
    real_data, labels, step_nb =create_emittor_comparison_with_cluster(real_clusters, ei)
    model = Sequential()
    model.add(LSTM(units=128, input_shape=(2, 50)))
    model.add(Dense(1, activation="sigmoid"))
    model.compile(loss='binary_crossentropy', optimizer='rmsprop', metrics=[
                  'accuracy', metrics.f1_score_threshold(), metrics.precision_threshold(), metrics.recall_threshold()])
    model.load_weights('./weights/my_model_clusters_weights.h5')

    to_predict=np.array(real_data)
    predictions=model.predict(to_predict)
    predictions=np.array([k[0] for k in predictions])
    labels=np.array(labels)
    thresholdlist=np.arange(50,2000,50)
    recall_0_list=[]
    recall_1_list=[]
    precision_0_list=[]
    precision_1_list=[]
    
    for k in thresholdlist:
        scores, true_predictions, true_labels=prediction_processing(predictions, labels, k, step_nb)
        recall_1_list.append(scores[0])
        recall_0_list.append(scores[1])
        precision_1_list.append(scores[2])
        precision_0_list.append(scores[3])
    fig=plt.figure(0)
    ax=fig.add_subplot(2,1,1)
    plt.plot(thresholdlist,recall_0_list, 'bo',thresholdlist,recall_1_list, 'ro')

    ax2=fig.add_subplot(2,1,2)

    plt.plot(thresholdlist,precision_0_list, 'bo',thresholdlist,precision_1_list, 'ro')
    plt.show()
    
    

if __name__=='__main__':
    test()

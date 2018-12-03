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

from processDL import create_clusters, create_emittor_comparison_with_cluster, create_cheat_comparison_with_cluster, create_comparison_one_to_one
from utils import config
WEIGHTS_DIR=config['PATH']['weights']

def train():
    """
    Builds fake data to train the model on it.
    Saves the weights calculated for the following tests
    """
    fake_data, fake_labels = multiple_fake_clusters(500, 50, 10, 10,20)
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
    model.save_weights(WEIGHTS_DIR+'/my_real_model_clusters_weights.h5')


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

def one_prediction(predictions, step_nb, threshold):
    number_sequences=step_nb//50
    total_prediction=0
    for i in range(number_sequences):
        total_prediction+=(1/predictions[i])
    if total_prediction>threshold:
        total_prediction=False
    else:
        total_prediction=True
    return(total_prediction)

def test():

    """
    Tests our model on unseen data. We need first to pre-process the data
    Shows the recall, precision for different thresholds on a graph.
    We can choose the weights of the training on real data or on fake data generated
    """
    real_clusters, ei = create_clusters()
    real_data, labels, step_nb =create_emittor_comparison_with_cluster(real_clusters, ei)
    print(labels)
    model = Sequential()
    model.add(LSTM(units=128, input_shape=(2, 50)))
    model.add(Dense(1, activation="sigmoid"))
    model.compile(loss='binary_crossentropy', optimizer='rmsprop', metrics=[
                  'accuracy', metrics.f1_score_threshold(), metrics.precision_threshold(), metrics.recall_threshold()])
    model.load_weights(WEIGHTS_DIR+'/my_model_clusters_weights.h5')

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

def are_in_same_cluster(id_emittor, id_cluster, ei, clusters):
    """
    Determines if an emittor is in a cluster by comparing the emittor emissions to the cluster emissions
    :param id_emittor: Id of the emittor to compare
    :param id_cluster: Id of the cluster to compare
    :param ei: List of the sampled emissions of all the emittors
    :param clusters: List of the clusters containing emittors ids
    """
    model = Sequential()
    model.add(LSTM(units=128, input_shape=(2, 50)))
    model.add(Dense(1, activation="sigmoid"))
    model.compile(loss='binary_crossentropy', optimizer='rmsprop', metrics=[
                  'accuracy', metrics.f1_score_threshold(), metrics.precision_threshold(), metrics.recall_threshold()])
    model.load_weights(WEIGHTS_DIR+'/my_real_model_clusters_weights.h5')
    list_of_data, step_nb=create_comparison_one_to_one(id_emittor, ei, clusters[id_cluster], 50)
    to_predict=np.array(list_of_data)
    prediction_on_sequence=model.predict(to_predict)
    final_prediction=one_prediction(prediction_on_sequence, step_nb, 1000)
    return(final_prediction)

    
    

if __name__=='__main__':
    real_clusters, ei = create_clusters()#will be given by backend in production
    for k in ei:
        for cluster in real_clusters:
            print("emittor %s in %s is %s"%(k,cluster,are_in_same_cluster(k,cluster,ei, real_clusters)))
            print('')
            
    
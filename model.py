from keras.models import Sequential
from keras.layers import LSTM, Dense
from keras.datasets import mnist
from keras.utils import np_utils
from keras.callbacks import TensorBoard
from keras import initializers
import utils as utils
import numpy as np
import itertools
from progressbar import ProgressBar
import csv
import pandas as pd
from time import time

tsexs1=utils.get_track_stream_exs_from_prp("prod/testDeep2.prp")

time_step_ms = 100

def init_weights(shape):
    return initializers.random_normal(shape)

def predict_all_ids(tsexs):
    raw_tracks = []
    stations_data = []
    for tsex in tsexs:
        raw_tracks = utils.get_track_stream_ex_info(tsex, raw_tracks)
    y_pred, ids = utils.get_dbscan_prediction(raw_tracks)
    stations_data.append([y_pred, ids])
    return [y_pred, ids]


def get_tracks_by_ids(tsexs, id1, id2):
    raw_tracks = []
    for tsex in tsexs:
        tracks = tsex.data.tracks
        for track in tracks:
            if track.id.most_significant == id1 or track.id.most_significant == id2:
                raw_tracks.append(utils.get_track_info_with_alternates(track))
    return raw_tracks

def get_last_track_by_id(tsexs, id):
    raw_tracks = []
    for tsex in tsexs:
        tracks = tsex.data.tracks
        for track in tracks:
            if track.id.most_significant == id: 
                raw_tracks = utils.get_track_info_with_alternates(track)
    return raw_tracks
                


def get_start_and_end(tsexs):
    raw_tracks = []
    for tsex in tsexs:
        tracks = tsex.data.tracks
        for track in tracks:
            raw_tracks.append(utils.get_track_info_with_alternates(track))
    start_date = raw_tracks[0][5][0][0]
    end_date = raw_tracks[-1][5][0][1]
    sequence_size = (end_date-start_date)/time_step_ms
    return(start_date, end_date, sequence_size)

def get_steps_track(tsexs, id, sequence_size, start_date_ms):
    last_track_id = get_last_track_by_id(tsexs, id)
    data = []
    for i in range(int(sequence_size)):
        found = 0
        for alternate in last_track_id[5]:
            if alternate[0] <= start_date_ms + i*time_step_ms <= alternate[1]:
                found = 1
                break
        data.append(found)
    return(data)

def process_data(tsexs):
    preds = predict_all_ids(tsexs)

    print(len(preds[0]))

    temporal_data = get_start_and_end(tsexs1)
    start_date_ms = temporal_data[0]
    end_date_ms = temporal_data[1]
    sequence_size = temporal_data[2]

    emitter_infos = {}
    print('Getting the steps from all the tracks')
    progress=0
    pbar = ProgressBar(maxval=(len(preds[0])))
    pbar.start()
    for i in range (len(preds[0])):
        emitter_infos[preds[1][i]] = {
            "network" : preds[0][i],
            "steps" : get_steps_track(tsexs1, preds[1][i], sequence_size, start_date_ms)
        }
        progress+=1
        pbar.update(progress)
        pbar.finish()
    print(len(emitter_infos))

    X = []
    Y = []
    print('Processing data')
    progress = 0
    pbar2 = ProgressBar(maxval=(len(preds[0])*len(preds[0]))/2)
    pbar2.start()
    for couple in itertools.combinations(preds[1],2):
        Y_value = int(emitter_infos[couple[0]]["network"]==emitter_infos[couple[1]]["network"])
        steps1 = get_steps_track(tsexs1, couple[0], sequence_size, start_date_ms)
        steps2 = get_steps_track(tsexs1, couple[1], sequence_size, start_date_ms)
        X_value = []
        for i in range (int(sequence_size)):
            X_value.append([steps1[i], steps2[i]])         
        #[get_steps_track(tsexs1, couple[0], sequence_size, start_date_ms), get_steps_track(tsexs1, couple[1], sequence_size, start_date_ms)]
        X.append(X_value)
        Y.append(Y_value)
        progress += 1
        pbar2.update(progress)
        #test_writer.writerow([X_value, Y_value])
    pbar2.finish()
    df = pd.DataFrame(
        {
            'X' : X,
            'Y' : Y
        }, columns = ['X', 'Y'])
    df.to_csv('test2.csv')

    print(np.array(X).shape)

    model = Sequential()
    model.add(LSTM(units = 32, input_shape=(6174 , 2)))
    model.add(Dense(1))

    model.compile(loss='mse', optimizer='rmsprop', metrics=['accuracy'])

    tensorboard = TensorBoard(log_dir="logs/{}".format(time()))

    model.fit(
        np.array(X),
        np.array(Y),
        batch_size=10,
        epochs=64,
        validation_split=0.05,
        callbacks=[tensorboard])

    

process_data(tsexs1)

df = pd.read_csv('test3.csv')
#print(df.info)

#print(df.dtypes)

print("Converting")
trainX = df['X']
trainY = df['Y']

#print(trainX.shape)


# model = Sequential()
# model.add(LSTM(input_dim = 1, output_dim = 32, input_shape=(6174 , 2)))
# model.add(Dense(1))

# model.compile(loss='mse', optimizer='rmsprop')

# model.fit(
#     trainX,
#     trainY,
#     batch_size=64,
#     nb_epoch=10,
#     validation_split=0.05)


#get_tracks_by_ids(tsexs1,predict_all_ids(tsexs1))

    # raw_tracks = utils.get_track_stream_ex_info(tsex, raw_tracks)
    # real_tracks.append(tsex.data.tracks)
# print((raw_tracks))
# y_pred, ids = utils.get_dbscan_prediction(raw_tracks)
# print(y_pred)
# stations_data.append([y_pred, ids, real_tracks])
# stations_data = np.array(stations_data)


""" # Hyper parameters
batch_size = 128
nb_epoch = 50

# Parameters for MNIST dataset
img_rows, img_cols = 28, 28
nb_classes = 10

# Parameters for LSTM network
nb_lstm_outputs = 30
nb_time_steps = img_rows
dim_input_vector = img_cols

# Load MNIST dataset
(X_train, y_train), (X_test, y_test) = mnist.load_data()
print('X_train original shape:', X_train.shape)
input_shape = (nb_time_steps, dim_input_vector)

X_train = X_train.astype('float32') / 255.
X_test = X_test.astype('float32') / 255.
Y_train = np_utils.to_categorical(y_train, nb_classes)
Y_test = np_utils.to_categorical(y_test, nb_classes)

print('X_train shape:', X_train.shape)
print(X_train.shape[0], 'train samples')
print(X_test.shape[0], 'test samples')

# Build LSTM network
model = Sequential()
model.add(LSTM(nb_lstm_outputs, input_shape=input_shape))
model.add(Dense(nb_classes, activation='softmax', kernel_initializer=init_weights(nb_classes)))
model.compile(optimizer='rmsprop', loss='categorical_crossentropy', metrics=['accuracy'])
model.summary()

history = model.fit(X_train, Y_train, nb_epoch=nb_epoch, batch_size=batch_size, shuffle=True, verbose=1)

# Evaluate
evaluation = model.evaluate(X_test, Y_test, batch_size=batch_size, verbose=1)
print('Summary: Loss over the test dataset: %.2f, Accuracy: %.2f' % (evaluation[0], evaluation[1]))
 """
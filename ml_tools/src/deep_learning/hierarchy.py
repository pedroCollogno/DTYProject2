from keras import Sequential
from keras.layers import LSTM, Dropout, Dense
import metrics
from keras.callbacks import TensorBoard, Callback, EarlyStopping
from time import time



def train_hierarchy():
    model=Sequential()
    model.add(LSTM(units=128, input_shape=(50,2)))
    model.add(Dropout(0.5))
    model.add(Dense(1, activation="sigmoid"))
    my_callbacks = [EarlyStopping(monitor='auc_roc', patience=300, verbose=1, mode='max'),
                    TensorBoard(log_dir="logs/{}".format(time()))]
    model.compile(loss='binary_crossentropy', optimizer='rmsprop', metrics=[
                  'accuracy', metrics.auc_roc, metrics.f1_score_threshold(), metrics.precision_threshold(), metrics.recall_threshold()])

    X=np.array([])
    Y=np.array([])

    model.fit(
            X,
            Y,
            batch_size=100,
            epochs=5,
            callbacks=my_callbacks,
            shuffle=True

    )
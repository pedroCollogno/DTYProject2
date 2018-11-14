from keras import backend as K
import tensorflow as tf


def precision_threshold(threshold=0.5):
    def precision(y_true, y_pred):
        """Precision metric.
         Only computes a batch-wise average of precision.
         Computes the precision, a metric for multi-label classification of
        how many selected items are relevant.
        """
        threshold_value = threshold
        y_pred = K.cast(K.greater(K.clip(y_pred, 0, 1), threshold_value), K.floatx())
        true_positives = K.sum(K.round(K.clip(y_true * y_pred, 0, 1)))
        predicted_positives = K.sum(K.round(K.clip(y_pred, 0, 1)))
        p = true_positives / (predicted_positives + K.epsilon())
        return p

    return precision


def f1_score_threshold(threshold=0.5):
    def f1_score(y_true, y_pred, beta=1):
        """Computes the F score.
         The F score is the weighted harmonic mean of precision and recall.
        Here it is only computed as a batch-wise average, not globally.
         This is useful for multi-label classification, where input samples can be
        classified as sets of labels. By only using accuracy (precision) a model
        would achieve a perfect score by simply assigning every class to every
        input. In order to avoid this, a metric should penalize incorrect class
        assignments as well (recall). The F-beta score (ranged from 0.0 to 1.0)
        computes this, as a weighted mean of the proportion of correct class
        assignments vs. the proportion of incorrect class assignments.
         With beta = 1, this is equivalent to a F-measure. With beta < 1, assigning
        correct classes becomes more important, and with beta > 1 the metric is
        instead weighted towards penalizing incorrect class assignments.
        """
        threshold_value = threshold
        if beta < 0:
            raise ValueError('The lowest choosable beta is zero (only precision).')
        # If there are no true positives, fix the F score at 0 like sklearn.
        if K.sum(K.round(K.clip(y_true, 0, 1))) == 0:
            return 0
        precision = precision_threshold(threshold_value)
        recall = recall_threshold(threshold_value)
        p = precision(y_true, y_pred)
        r = recall(y_true, y_pred)
        bb = beta ** 2
        fbeta_score = (1 + bb) * (p * r) / (bb * p + r + K.epsilon())
        return fbeta_score

    return f1_score


def recall_threshold(threshold=0.5):
    def recall(y_true, y_pred):
        """Recall metric.
         Only computes a batch-wise average of recall.
         Computes the recall, a metric for multi-label classification of
        how many relevant items are selected.
        """
        threshold_value = threshold
        y_pred = K.cast(K.greater(K.clip(y_pred, 0, 1), threshold_value), K.floatx())
        true_positives = K.sum(K.round(K.clip(y_true * y_pred, 0, 1)))
        possible_positives = K.sum(K.round(K.clip(y_true, 0, 1)))
        r = true_positives / (possible_positives + K.epsilon())
        return r

    return recall

# define roc_callback, inspired by https://github.com/keras-team/keras/issues/6050#issuecomment-329996505
def auc_roc(y_true, y_pred):
    # any tensorflow metric
    value, update_op = tf.contrib.metrics.streaming_auc(y_pred, y_true)

    # find all variables created for this metric
    metric_vars = [i for i in tf.local_variables() if 'auc_roc' in i.name.split('/')[1]]

    # Add metric variables to GLOBAL_VARIABLES collection.
    # They will be initialized for new session.
    for v in metric_vars:
        tf.add_to_collection(tf.GraphKeys.GLOBAL_VARIABLES, v)

    # force to update metric values
    with tf.control_dependencies([update_op]):
        value = tf.identity(value)
        return value


def get_metrics(threshold):
    return {
        'precision': precision_threshold(threshold=threshold),
        'recall': recall_threshold(threshold=threshold),
        'f1_score': f1_score_threshold(threshold=threshold)
    }
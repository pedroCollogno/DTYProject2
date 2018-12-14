import numpy as np
import random
from progressbar import ProgressBar
from time import time


def fake_data_generator(sequence_size, n_clusters, avg_n_emitters_in_clusters, silence_time):
    """ Creates fake clusters, emitters and emissions with a certain sequence_size

    :param sequence_size: Size of the sequence built by the function
    :param n_clusters: Number of clusters to build
    :param avg_n_emitters_in_clusters: Number of emitters in a cluster
    :param silence_time: A number determining how much time the network remains silent (silence_time/n_emitters: probability)
    :return: A list of clusters containing a list of emissions indexed by emitter_id
    """
    clusters = []
    for i in range(n_clusters):
        sum = sequence_size
        n = avg_n_emitters_in_clusters+1
        rnd_array = np.random.multinomial(sum, np.concatenate((np.ones(n-1)/(n+silence_time-1), np.array(
            [silence_time/(n+silence_time-1)]))), size=1)[0] 
        fake_X = [-1 for j in range(sequence_size)]
        count_visited = 0

        for a in range(n):
            places_in_sequence = sorted(random.sample(
                range(sequence_size-count_visited), rnd_array[a]))
            count_visited += rnd_array[a]
            b = 0
            count_free = 0
            tracer = 0
            while b < rnd_array[a]:
                if (fake_X[tracer] == -1 and places_in_sequence[b] == count_free and a != 0):
                    fake_X[tracer] = a
                    count_free += 1
                    b += 1
                elif (fake_X[tracer] == -1):
                    count_free += 1
                tracer += 1

        emissions = {}
        for k in range(1, n):
            emissions["cluster_"+str(i)+"_emitter_" +
                      str(k)] = [int(i == k) for i in fake_X]
        clusters.append(emissions)
    return(clusters)


def create_cluster_comparison(sequence_size, n_clusters, avg_n_emitters_in_clusters, silence_time):
    """
    Uses the fake clusters generated to build data to train the deep_learning algorithm
    :param sequence_size: Size of the sequence built by the function$
    :param n_clusters: Number of clusters to build
    :param avg_n_emitters_in_clusters: Number of emitters in a cluster
    :param silence_time: Number which determines the amount of time a cluster should remain silent
    :return: The comparison of every emitter to the total emission of every cluster and if it belongs to it
    """
    clusters = fake_data_generator(
        sequence_size, n_clusters, avg_n_emitters_in_clusters, silence_time)
    labels = []
    data_for_deep = []
    for cluster in clusters:
        for emitter in cluster:
            for cluster_secondary in clusters:
                if cluster_secondary == cluster:
                    label = True
                else:
                    label = False
                data = [0 for k in range(sequence_size)]
                for emitter_secondary in cluster_secondary:
                    if (emitter_secondary != emitter):
                        data = [int(data[k] or cluster_secondary[emitter_secondary][k])
                                for k in range(sequence_size)]
                data_for_deep.append([cluster[emitter], data])
                labels.append(label)
    return(labels, data_for_deep)


def multiple_fake_clusters(n_samples, sequence_size, n_clusters, avg_n_emitters_in_clusters, silence_time):
    """
    Creates multiple different situations with the previous functions
    :param n_samples: Number of situations to be created
    :param sequence_size: Sequence size of the emitters to create
    :param n_clusters: Number of clusters per situation created
    :param avg_n_emitters_in_clusters: Number of emitters per cluster
    param silence_time: Number which determines the amount of time a cluster should remain silent
    :return: A list of comparison between emitter emission and cluster emissions and if the emitter belongs to the cluster
    """
    full_labels = []
    full_data = []
    for k in range(n_samples):
        labels, data_for_deep = create_cluster_comparison(
            sequence_size, n_clusters, avg_n_emitters_in_clusters, silence_time)
        full_labels = full_labels+labels
        full_data = full_data+data_for_deep
    return(full_data, full_labels)

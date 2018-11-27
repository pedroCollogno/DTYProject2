import numpy as np
import random
from progressbar import ProgressBar
from time import time

def fake_data_generator(sequence_size,n_clusters, avg_n_emittors_in_clusters):
    """
    Creates fake clusters, emittors and emissions with a certain sequence_size
    :param sequence_size: Size of the sequence built by the function
    :param n_clusters: Number of clusters to build
    :param avg_n_emitros_in_clusters: Number of emittors in a cluster
    :return: A list of clusters containing a list of emissions indexed by emittor_id
    """
    clusters=[]
    for i in range(n_clusters):
        sum=sequence_size
        n=avg_n_emittors_in_clusters+1
        rnd_array=np.random.multinomial(sum,np.concatenate((np.ones(n-1)/(n+9), np.array([20/(n+19)]))), size=1)[0]#20 corresponds to the silence time in each sequence
        fake_X=[-1 for j in range(sequence_size)]
        count_visited=0
        for a in range(n):
            places_in_sequence=sorted(random.sample(range(sequence_size-count_visited), rnd_array[a]))
            count_visited+=rnd_array[a]
            b=0
            count_free=0
            tracer=0
            while b<rnd_array[a]:
                if (fake_X[tracer]==-1 and places_in_sequence[b]==count_free and a!=0):
                    fake_X[tracer]=a
                    count_free+=1
                    b+=1
                elif (fake_X[tracer]==-1):
                    count_free+=1
                tracer+=1
            emissions={}
        for k in range(1,n):
            emissions["cluster_"+str(i)+"_emittor_"+str(k)]=[int(i==k) for i in fake_X]
        clusters.append(emissions)
    return(clusters)

def create_cluster_comparison(sequence_size, n_clusters, avg_n_emittors_in_clusters):
    """
    Uses the fake clusters generated to build data to train the deep_learning algorithm
    :param sequence_size: Size of the sequence built by the function$
    :param n_clusters: Number of clusters to build
    :param avg_n_emitros_in_clusters: Number of emittors in a cluster
    :return: The comparison of every emittor to the total emission of every cluster and if it belongs to it
    """
    clusters=fake_data_generator(sequence_size, n_clusters, avg_n_emittors_in_clusters)
    labels=[]
    data_for_deep=[]
    for cluster in clusters:
        for emittor in cluster:
            for cluster_secondary in clusters:
                if cluster_secondary==cluster:
                    label=True
                else:
                    label=False
                data=[0 for k in range(sequence_size)]
                for emittor_secondary in cluster_secondary:
                    if (emittor_secondary!=emittor):
                        data=[int(data[k] or cluster_secondary[emittor_secondary][k]) for k in range(sequence_size)]
                data_for_deep.append([cluster[emittor],data])
                labels.append(label)
    return(labels, data_for_deep)

def multiple_fake_clusters(n_samples, sequence_size, n_clusters, avg_n_emittors_in_clusters):
    """
    Creates multiple different situations with the previous functions
    :param n_samples: Number of situations to be created
    :param sequence_size: Sequence size of the emittors to create
    :param n_clusters: Number of clusters per situation created
    :param avg_n_emittors_in_clusters: Number of emittors per cluster
    :return: A list of comparison between emittor emission and cluster emissions and if the emittor belongs to the cluster
    """
    full_labels=[]
    full_data=[]
    for k in range(n_samples):
        labels,data_for_deep=create_cluster_comparison(sequence_size, n_clusters,avg_n_emittors_in_clusters)
        full_labels=full_labels+labels
        full_data=full_data+data_for_deep
    return(full_data,full_labels)

        









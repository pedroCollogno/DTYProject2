import numpy as np
import random
from progressbar import ProgressBar
from time import time

def fake_data_generator(sequence_size,n_clusters, avg_n_emittors_in_clusters):
    clusters=[]
    for i in range(n_clusters):
        sum=sequence_size
        n=avg_n_emittors_in_clusters+1
        rnd_array=np.random.multinomial(sum, np.ones(n)/n, size=1)[0]
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
                elif (fake_X[tracer]==-1 and places_in_sequence[b]==count_free and a==0):
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
    full_labels=[]
    full_data=[]
    for k in range(n_samples):
        labels,data_for_deep=create_cluster_comparison(sequence_size, n_clusters,avg_n_emittors_in_clusters)
        full_labels=full_labels+labels
        full_data=full_data+data_for_deep
    return(full_data,full_labels)

        









import random
import numpy as np
def fake_terrorist_network( n_emittors_per_cluster, full_sequence_size, silence_time):
    big_chef=random.randint(0,1)
    small_chefs=random.randint(0,3)
    shit_units=n_emittors_per_cluster-big_chef-small_chefs
    if big_chef==1:
        talk_big_chef=random.randint(20,60)
        if talk_big_chef>50:
            talk_small_chef=random.randint(15,20)
        else:
            talk_small_chef=random.randint(20,25)
        talk_shit_units=100-talk_big_chef-talk_small_chef
    
    else:
        talk_small_chef=random.randint(20, 20*(small_chefs+1))
        talk_shit_units=100-talk_small_chef
    mat_of_network=[-1]
    mat_of_talk_times=[silence_time]
    if big_chef!=0:
        mat_of_network.append(1)
        mat_of_talk_times.append(talk_big_chef)
    for k in range(small_chefs):
        mat_of_network.append(100+k)
        mat_of_talk_times.append(talk_small_chef/small_chefs)
    for j in range(shit_units):
        mat_of_network.append(1000+j)
        mat_of_talk_times.append(talk_shit_units/shit_units)
    talk_ditribution=[]
    for k in range(full_sequence_size):
        talking=random.choices(mat_of_network,mat_of_talk_times)[0]
        talk_ditribution.append(talking)
    return(mat_of_network,talk_ditribution)

def create_fake_sequences(n_clusters, full_sequence_size, silence_time):
    list_of_data=[]
    list_of_labels=[]
    for k in range(n_clusters):
        network,talk_distribution=fake_terrorist_network(10,full_sequence_size, silence_time)
        for emittor in network[1:]:
            emittor_emission=[int(i==emittor) for i in talk_distribution]
            list_of_data.append([emittor_emission])
            if emittor==1:
                list_of_labels.append(0)
            elif emittor<1000 and emittor>=100:
                list_of_labels.append(1)
            else:
                list_of_labels.append(2)
    return(list_of_data, list_of_labels)



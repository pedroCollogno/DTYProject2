import random
import numpy as np
def fake_hierarchy_network( n_emitters_per_cluster, full_sequence_size, silence_time):
    """Creates a network cluster of enemy emitters and their emissions
    :param n_emitters_per_cluster: Number of emitters in the network to be created
    :param full_sequence_size: The size of the talking sequence for this network
    :param silence_time: The time percentage during which the network remains silent
    :return: The network structure and the speaking times
    """
    big_chef=random.randint(0,1)
    if big_chef==0:
        small_chefs=random.randint(2,3)
        small_units=n_emitters_per_cluster-big_chef-small_chefs
    else:
        small_chefs=random.randint(0,3)
        small_units=n_emitters_per_cluster-big_chef-small_chefs
    if big_chef==1:
        talk_big_chef=random.randint(20,60)
        if talk_big_chef>50:
            talk_small_chef=random.randint(15,20)
        else:
            talk_small_chef=random.randint(20,25)
        talk_small_units=100-talk_big_chef-talk_small_chef
    
    else:
        if small_chefs!=0:
            talk_small_chef=random.randint(20, 20*(small_chefs+1))
        else:
            talk_small_chef=0
        talk_small_units=100-talk_small_chef
    mat_of_network=[-1]
    mat_of_talk_times=[silence_time]
    if big_chef!=0:
        mat_of_network.append(1)
        mat_of_talk_times.append(talk_big_chef)
    for k in range(small_chefs):
        mat_of_network.append(100+k)
        mat_of_talk_times.append(talk_small_chef/small_chefs)
    for j in range(small_units):
        mat_of_network.append(1000+j)
        mat_of_talk_times.append(talk_small_units/small_units)
    talk_ditribution=[]
    for k in range(full_sequence_size):
        talking=random.choices(mat_of_network,mat_of_talk_times)[0]
        talk_ditribution.append(talking)
    print(talk_ditribution)
    return(mat_of_network,talk_ditribution)

def create_fake_sequences(n_clusters, full_sequence_size, silence_time):
    """Creates several enemy networks and labels the emissions in the hierarchy
    :param n_clusters: The amount of clusters to be created
    :param full_sequence_size: The duration of a network speaking sequence
    :param silence_time: The time percentage during which a network remains silent
    :return: A list of emissions and their importance in the hierarchy
    """
    list_of_data=[]
    list_of_labels=[]
    for k in range(n_clusters):
        network,talk_distribution=fake_hierarchy_network(10,full_sequence_size, silence_time)
        for emitter in network[1:]:
            emitter_emission=[int(i==emitter) for i in talk_distribution]
            list_of_data.append(emitter_emission)
            if emitter==1:
                list_of_labels.append(0)
            elif emitter<1000 and emitter>=100:
                list_of_labels.append(1)
            else:
                list_of_labels.append(2)
    return(list_of_data, list_of_labels)

def fake_hierarchy_emission(sequence_size, number_to_create):
    created_emissions=[]
    created_labels=[]
    for j in range(number_to_create):
        i=random.randint(0,sequence_size-1)
        list_of_emitting=random.sample(range(sequence_size), i)
        list_of_emissions=[0 for k in range(sequence_size)]
        for k in range(sequence_size):
            if k in list_of_emitting:
                list_of_emissions[k]=1
        importance=(i-i%10)/10
        created_emissions.append(list_of_emissions)
        created_labels.append(importance)
    return(created_emissions,created_labels)
        





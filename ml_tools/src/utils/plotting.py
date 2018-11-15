import matplotlib.pyplot as plt
from .loading import get_track_stream_exs_from_prp

def display_alternates(*args):
    """ Function that displays all the alternates detected by a station

    :args: the prp files from all the stations
    """
    prps = [get_track_stream_exs_from_prp(args[i]) for i in range(len(args))]
    all_alternates = {}
    for i in range(len(prps)):
        all_alternates_current_prp = {}
        for tsex in prps[i]:
            if tsex.data.tracks:
                for track in tsex.data.tracks:
                    key_id = track.id.most_significant
                    all_alternates_current_prp[key_id] = track.alternates
                    """ if key_id in all_alternates_current_prp:
                        all_alternates_current_prp[key_id].append(current_alternate)
                    else:
                        all_alternates_current_prp[key_id] = [current_alternate] """
        all_alternates["prp{}".format(i + 1)] = all_alternates_current_prp

    fig, ax = plt.subplots(len(args), sharex=True)
    for i in range(len(args)):

        key_indice = 1
        y_labels = []
        y_ticks = []
        for key in all_alternates["prp{}".format(i+1)]:
            boxes = []
            for alternate in all_alternates["prp{}".format(i+1)][key]:
                boxes.append((alternate.start.date_ms/(1000),
                              alternate.duration_us/1000000))
            ax[i].broken_barh(boxes, (key_indice, 0.9), facecolors='blue')
            y_ticks.append(key_indice)
            y_labels.append(str(key))
            key_indice += 1
        ax[i].set_yticks(y_ticks)
        ax[i].set_yticklabels(y_labels)
        ax[i].set_ylabel("Id")
        ax[i].set_xlabel("Seconds")
    plt.show()

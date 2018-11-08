import gen.TrackstreamEx_pb2 as ts
import os

from progressbar import ProgressBar


def read_prp(filepath):
    """Reads a .prp file, frame after frame, and returns an array of frames

    :param filepath: path to the .prp file to read
    :return: the list of all frames in the .prp file
    """
    print("\nReading .prp file from path %s" % filepath)
    frames = []
    with open(filepath, "rb") as f:
        file_size = os.path.getsize(filepath)
        progress = 0
        pbar = ProgressBar(maxval=file_size)
        pbar.start()
        while(file_size > progress):
            header_bytes = f.read(4)
            next_bytes = f.read(8)
            identification_bytes = f.read(4)

            data_type_bytes = f.read(2)
            data_type = int.from_bytes(data_type_bytes, byteorder='little')

            size_bytes = f.read(4)
            size = int.from_bytes(size_bytes, byteorder='little')

            track_stream_bytes = f.read(size)
            footer_bytes = f.read(4)
            ending_bytes = f.read(4)

            frame = {
                'header': header_bytes,
                'next': next_bytes,
                'identification': identification_bytes,
                'data_type': data_type,
                'size': size,
                'data': track_stream_bytes,
                'footer': footer_bytes,
                'ending': ending_bytes
            }
            frames.append(frame)

            frame_size = 4+8+4+2+4+size+4+4
            progress += frame_size
            pbar.update(progress)
        pbar.finish()
    print("Done ! Found %s frames in the file.\n" % len(frames))
    return(frames)


def get_track_stream_exs_from_prp(filepath):
    """Reads a .prp file, and takes TrackStreamEx objects from it

    :param filepath: path to the .prp file to read
    :return: the list of all TrackStreamEx objects in the .prp file
    """
    frames = read_prp(filepath)
    track_stream_exs = []
    for frame in frames:
        if frame['data_type'] == 518:
            TSEX = ts.TrackStreamEx()
            TSEX.ParseFromString(frame['data'])
            track_stream_exs.append(TSEX)
    return(track_stream_exs)

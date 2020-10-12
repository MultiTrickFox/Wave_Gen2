import config
from ext import pickle_save, pickle_load

from glob import glob
from random import shuffle

from librosa.core import load

from torch import Tensor

from scipy.io.wavfile import write

##


def save_data():
    pickle_save([load(file,config.sample_rate)[0] for file in glob(config.data_path+'/*.wav')], config.data_path+'.pk')

def load_data():
    data = [Tensor(sequence[:config.frame_len+ (len(sequence)-config.frame_len)//config.frame_stride*config.frame_stride])
                .view(1, -1, 1)
                    for sequence in pickle_load(config.data_path+'.pk')]
    if config.use_gpu:
        data = [sequence.cuda() for sequence in data]
    frames = [[sequence[:,i*config.frame_stride:i*config.frame_stride+config.frame_len,:]
             for i in range((sequence.size(1)-config.frame_len)//config.frame_stride + 1)]
                    for sequence in data]
    return frames


def split_data(data, dev_ratio=None, do_shuffle=False):
    if not dev_ratio: dev_ratio = config.dev_ratio
    if do_shuffle: shuffle(data)
    if dev_ratio:
        hm_train = int(len(data)*(1-dev_ratio))
        data_dev = data[hm_train:]
        data = data[:hm_train]
        return data, data_dev
    else:
        return data, []

def batchify_data(data, batch_size=None, do_shuffle=True):
    if not batch_size: batch_size = config.batch_size
    if do_shuffle: shuffle(data)
    hm_batches = int(len(data)/batch_size)
    return [data[i*batch_size:(i+1)*batch_size] for i in range(hm_batches)] \
        if hm_batches else [data]


def file_output(file, sequence):
    sequence.resize(sequence.shape[2])
    write(f'{file}.wav', config.sample_rate, sequence)


##


def main():
    save_data()


if __name__ == '__main__':
    main()

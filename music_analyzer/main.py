# %%
import librosa
import librosa.display
import numpy as np
import matplotlib.pyplot as plt

import os

from utils import *

# %%
f_path = os.path.join("audios", "GALA - Young For You.mp3")
y, fs = load_audio(f_path)

# %%
def plot_beats(y, fs, begin=0, end=10, hop_length=512):
    y_ = y[int(begin * fs): int(end * fs)]

    onset_env = librosa.onset.onset_strength(y_, fs, aggregate=np.median)
    tempo, beats = librosa.beat.beat_track(onset_envelope=onset_env, sr=fs, hop_length=hop_length)
    times = librosa.times_like(onset_env, sr=fs, hop_length=hop_length) + begin

    # plot
    plt.figure(figsize=(9, 6))
    fig, ax = plt.subplots(nrows=2, sharex=True, figsize=(9, 6))
    M = librosa.feature.melspectrogram(y=y_, sr=fs, hop_length=hop_length)
    librosa.display.specshow(librosa.power_to_db(M, ref=np.max), y_axis='mel', x_axis='time', hop_length=hop_length,
                             ax=ax[0])
    # waveform
    t = np.arange(begin, end, 1 / fs)
    ax[1].plot(t, y_)
    ax[1].vlines(times[beats], 0, 1, color='r', linestyles='--')
    plt.show()



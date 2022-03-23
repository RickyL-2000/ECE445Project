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
    fig, ax = plt.subplots(nrows=3, figsize=(12, 12))
    M = librosa.feature.melspectrogram(y=y_, sr=fs, hop_length=hop_length)
    M = librosa.power_to_db(M, ref=np.max)
    librosa.display.specshow(M, y_axis='mel', x_axis='time', hop_length=hop_length, ax=ax[0])
    ax[0].set_xlim(begin, end)
    ax[0].set_xlabel('')    # cancel x label
    ax[0].set_title("Mel Spectrogram")

    # waveform
    t = np.arange(begin, end, 1 / fs)
    ax[1].plot(t, y_, label='waveform')
    ax[1].set_xlabel('TIME')
    ax[1].vlines(times[beats], 0, 1, color='r', linestyles='--', label='beat')
    # energy
    energy = librosa.feature.rms(y_, frame_length=2048, hop_length=hop_length)[0]
    times = librosa.times_like(energy, sr=fs, hop_length=hop_length) + begin
    ax[1].plot(times, energy, color='y', label='energy')
    ax[1].set_xlim(begin, end)
    ax[1].legend()
    ax[1].set_title("Waveform Feature")

    # color map
    color_map = np.zeros_like(energy)
    beat_sequence = np.zeros_like(energy)
    beat_sequence[beats] = 1.0
    beat_gap = 60 / tempo * fs / hop_length
    energy /= np.max(energy)
    beat_soft = np.convolve(beat_sequence, np.hamming(2 * beat_gap * 0.4), mode='same')
    color_map += energy + 0.3 * beat_soft
    color_map /= np.max(color_map)
    color_map = np.convolve(color_map, np.ones(16) / 16, mode='same')  # filter
    color_matrix = np.tile(color_map, (int(color_map.shape[0] / 4), 1))
    color_matrix = 1 - color_matrix
    ax[2].imshow(color_matrix, cmap='hsv')
    ax[2].set_title("Color Sequence")

    plt.show()

plot_beats(y, fs, begin=0, end=10, hop_length=512)

# %%
begin = 0
end = 10
hop_length = 512
# slice
y_ = y[int(begin * fs): int(end * fs)]
# extract onset envelope
onset_env = librosa.onset.onset_strength(y_, fs, aggregate=np.median)
# extract beat sequence
tempo, beats = librosa.beat.beat_track(onset_envelope=onset_env, sr=fs, hop_length=hop_length)
times = librosa.times_like(onset_env, sr=fs, hop_length=hop_length) + begin

# plot
# mel spectrogram
plt.figure(figsize=(9, 6))
fig, ax = plt.subplots(nrows=2, sharex=True, figsize=(12, 9))
M = librosa.feature.melspectrogram(y=y_, sr=fs, hop_length=hop_length)
M = librosa.power_to_db(M, ref=np.max)
librosa.display.specshow(M, y_axis='mel', x_axis='time', hop_length=hop_length,
                         ax=ax[0])
# waveform
t = np.arange(begin, end, 1 / fs)
ax[1].plot(t, y_, label='waveform')
# beat mark
ax[1].vlines(times[beats], 0, 1, color='r', linestyles='--', label='beat')

# energy
energy = librosa.feature.rms(y_, frame_length=2048, hop_length=hop_length)[0]
times = librosa.times_like(energy, sr=fs, hop_length=hop_length) + begin
ax[1].plot(times, energy, color='y', label='energy')

plt.legend()
plt.show()

# %%
color_map = np.zeros_like(energy)
bright_map = np.zeros_like(energy)
beat_sequence = np.zeros_like(energy)
beat_sequence[beats] = 1.0
beat_gap = 60 / tempo * fs / hop_length

energy /= np.max(energy)
beat_soft = np.convolve(beat_sequence, np.hamming(2 * beat_gap * 0.4), mode='same')
color_map += energy + 0.3 * beat_soft
color_map /= np.max(color_map)
color_map = np.convolve(color_map, np.ones(8) / 8, mode='same')  # filter
# color_map = 1 - color_map
color_map[0] = 0.0

color_matrix = np.tile(color_map, (int(color_map.shape[0]/4), 1))
# rgb_matrix = np.zeros((color_matrix.shape[0], color_matrix.shape[1], 3))
# rgb_matrix[:, :, 0] = color_matrix
# rgb_matrix[:, :, 0] = color_matrix
# rgb_matrix[:, :, 0] = color_matrix
# rgb_matrix * 255

plt.imshow(color_matrix, cmap='hsv')
# plt.scatter(times, np.zeros_like(energy), c=color_map, cmap=plt.cm.hsv, s=40)
plt.show()

# %%
# try filter
color_map_ = np.convolve(color_map, np.ones(16) / 16, mode='same')
plt.plot(times, color_map_)
plt.show()

# %%
# try convolve beat sequence
beat_sequence_ = np.convolve(beat_sequence, np.hamming(2 * beat_gap * 0.4), mode='same')
plt.vlines(times[beats], 0, 1, color='r', linestyles='--', label='beat')
plt.plot(times, beat_sequence_)
plt.show()

# %%
# try plot together
begin = 0
end = 10
hop_length = 512

y_ = y[int(begin * fs): int(end * fs)]

onset_env = librosa.onset.onset_strength(y_, fs, aggregate=np.median)
tempo, beats = librosa.beat.beat_track(onset_envelope=onset_env, sr=fs, hop_length=hop_length)
times = librosa.times_like(onset_env, sr=fs, hop_length=hop_length) + begin

# plot
plt.figure(figsize=(9, 6))
fig, ax = plt.subplots(nrows=3, figsize=(12, 12))
M = librosa.feature.melspectrogram(y=y_, sr=fs, hop_length=hop_length)
M = librosa.power_to_db(M, ref=np.max)
librosa.display.specshow(M, y_axis='mel', x_axis='time', hop_length=hop_length, ax=ax[0])
ax[0].set_xlim(begin, end)

# waveform
t = np.arange(begin, end, 1 / fs)
ax[1].plot(t, y_, label='waveform')
ax[1].vlines(times[beats], 0, 1, color='r', linestyles='--', label='beat')

# energy
energy = librosa.feature.rms(y_, frame_length=2048, hop_length=hop_length)[0]
times = librosa.times_like(energy, sr=fs, hop_length=hop_length) + begin
ax[1].plot(times, energy, color='y', label='energy')
ax[1].set_xlim(begin, end)

plt.legend()

# color map
color_map = np.zeros_like(energy)
beat_sequence = np.zeros_like(energy)
beat_sequence[beats] = 1.0
beat_gap = 60 / tempo * fs / hop_length
energy /= np.max(energy)
beat_soft = np.convolve(beat_sequence, np.hamming(2 * beat_gap * 0.4), mode='same')
color_map += energy + 0.3 * beat_soft
color_map /= np.max(color_map)
color_map = np.convolve(color_map, np.ones(8) / 8, mode='same')  # filter
color_matrix = np.tile(color_map, (int(color_map.shape[0] / 4), 1))
ax[2].imshow(color_matrix, aspect='auto', cmap='hsv')

plt.show()

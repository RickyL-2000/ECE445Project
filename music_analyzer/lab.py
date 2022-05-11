# %%
import torch
from torch import package
import librosa
import librosa.display
import numpy as np
import matplotlib.pyplot as plt

import os
import sys

from utils import *
from mood_recog.inference import inference

# %%
f_path = os.path.join("audios", "GALA - Young For You.mp3")
y, fs = load_audio(f_path)

base_dir = 'D:/ECE445Project/music_analyzer'

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
    # ax[0].set_xlim(begin, end)
    # ax[0].set_xticks(np.arange(0, end-begin, (end-begin)/5), labels=list(np.arange(begin, end, (end-begin)/5)))
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
    color_map += energy + 0.6 * beat_soft
    color_map /= np.max(color_map)
    color_map = np.convolve(color_map, np.ones(32) / 32, mode='same')  # filter
    color_matrix = np.tile(color_map, (int(color_map.shape[0] / 4), 1))
    color_matrix = 1 - color_matrix
    ax[2].imshow(color_matrix, cmap='hsv')
    ax[2].set_title("Color Sequence")

    plt.show()

# plot_beats(y, fs, begin=10, end=20, hop_length=512)


# %%
def main(f_path, fs, hop_length=512):
    # f_path = os.path.join("audios", "GALA - Young For You.mp3")
    y, fs = load_audio(f_path, fs)

    # beat tracking
    onset_env = librosa.onset.onset_strength(y, fs, aggregate=np.median)
    tempo, beats = librosa.beat.beat_track(onset_envelope=onset_env, sr=fs, hop_length=hop_length)
    times = librosa.times_like(onset_env, sr=fs, hop_length=hop_length)

    # energy
    energy = librosa.feature.rms(y, frame_length=2048, hop_length=hop_length)[0]

    # color map
    hue_map = np.zeros_like(energy)
    value_map = np.zeros_like(energy)
    beat_sequence = np.zeros_like(energy)
    beat_sequence[beats] = 1.0
    beat_gap = 60 / tempo * fs / hop_length
    energy /= np.max(energy)
    beat_soft = np.convolve(beat_sequence, np.hamming(2 * beat_gap * 0.4), mode='same')
    hue_map += energy + 0.6 * beat_soft
    hue_map = np.convolve(hue_map, np.ones(32) / 32, mode='same')  # filter
    hue_map /= np.max(hue_map)
    # hue_map = np.convolve(hue_map, np.ones(32) / 32, mode='same')  # filter
    hue_map *= 360
    value_map += energy + 1 * beat_soft
    value_map = np.convolve(value_map, np.ones(32) / 32, mode='same')  # filter
    value_map /= np.max(value_map)
    # value_map = np.convolve(value_map, np.ones(32) / 32, mode='same')  # filter

    r, g, b = hsv2rgb(hue_map, np.ones_like(hue_map), value_map)

    with open(base_dir + "/output.txt", "w") as f:
        f.write(f"{fs / hop_length:.2f}\n")
        for i in range(r.shape[0]):
            f.write(f"{int(r[i])} {int(g[i])} {int(b[i])}\n")

# %%
# if __name__ == "__main__":
#     main(f_path=f_path, fs=22050, hop_length=512)
#     output2C(base_dir)

# %%
sys.exit()

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
# try plot together
# try emotion recog
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

# plt.legend()

# neural network
y__ = y[:]
mel = librosa.feature.melspectrogram(y=y__, sr=fs, n_fft=512, hop_length=256, win_length=512, fmax=8000)
mel = librosa.power_to_db(mel, ref=np.max)
imp = package.PackageImporter(f"{base_dir}/mood_recog/model.pt")
model = imp.load_pickle("emotion_recog", "model.pt")
emotion = inference(model, mel)

# color map
hue_map = np.zeros_like(energy)
value_map = np.zeros_like(energy)
beat_sequence = np.zeros_like(energy)
beat_sequence[beats] = 1.0
beat_gap = 60 / tempo * fs / hop_length
energy /= np.max(energy)
beat_soft = np.convolve(beat_sequence, np.hamming(2 * beat_gap * 0.4), mode='same')
hue_map += energy + 0.6 * beat_soft
hue_map = np.convolve(hue_map, np.ones(32) / 32, mode='same')  # filter
hue_map /= np.max(hue_map)
# hue_map = np.convolve(hue_map, np.ones(32) / 32, mode='same')  # filter
hue_map *= 360
value_map += energy + 1 * beat_soft
value_map = np.convolve(value_map, np.ones(32) / 32, mode='same')  # filter
value_map /= np.max(value_map)

color_matrix = np.tile(hue_map, (int(hue_map.shape[0] / 4), 1))
ax[2].imshow(color_matrix, aspect='auto', cmap='hsv')

plt.suptitle(f"emotion classified as Q{emotion+1}", fontdict={'weight': 'normal', 'size': 100})
plt.show()

# %% try output

y, fs = load_audio(f_path, fs)

y = y[int(0 * fs): int(10 * fs)]

hop_length = 512

# beat tracking
onset_env = librosa.onset.onset_strength(y, fs, aggregate=np.median)
tempo, beats = librosa.beat.beat_track(onset_envelope=onset_env, sr=fs, hop_length=hop_length)
times = librosa.times_like(onset_env, sr=fs, hop_length=hop_length)

# energy
energy = librosa.feature.rms(y, frame_length=2048, hop_length=hop_length)[0]

# color map
hue_map = np.zeros_like(energy)
value_map = np.zeros_like(energy)
beat_sequence = np.zeros_like(energy)
beat_sequence[beats] = 1.0
beat_gap = 60 / tempo * fs / hop_length
energy /= np.max(energy)
beat_soft = np.convolve(beat_sequence, np.hamming(2 * beat_gap * 0.4), mode='same')
hue_map += energy + 0.6 * beat_soft
hue_map /= np.max(hue_map)
hue_map = np.convolve(hue_map, np.ones(32) / 32, mode='same')  # filter
hue_map *= 360
value_map += energy + 0.3 * beat_soft
value_map = value_map / np.max(value_map) * 0.4 + 0.6
value_map = np.convolve(value_map, np.ones(32) / 32, mode='same')  # filter

r, g, b = hsv2rgb(hue_map, np.ones_like(hue_map), value_map)

with open(base_dir + "/output.txt", "w") as f:
    f.write(f"{fs / hop_length:.2f}\n")
    for i in range(r.shape[0]):
        f.write(f"{int(r[i])} {int(g[i])} {int(b[i])}\n")

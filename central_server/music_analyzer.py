import queue

import torch
from torch import package
import librosa
import numpy as np
import math
import time
import os

from utils.signal import *

class MusicAnalyzer:
    def __init__(self):
        imp = package.PackageImporter("model.pt")
        self.recognizer = imp.load_pickle("emotion_recog", "model.pt")

        self.rgb_seq = []
        self.hsv_seq = []
        self.sr = 0.0

        self.rgb_cache = []
        self.hsv_cache = []

    def emotion_recog(self, mel, channel=80):
        mel = mel[:channel, :]
        mel = torch.tensor(mel).to(torch.float32).unsqueeze(0)

        self.recognizer.eval()
        y_ = self.recognizer(mel)
        y_ = torch.argmax(y_, -1).numpy()

        return y_[0]

    def gen_color_seq(self, f_path, hop_length=512, n_fft=2048, win_length=2048):
        """
        Timing analysis:
            Start analyzing...
            Init time: 7.125805854797363s
            beats time: 1.3990507125854492s
            energy time: 0.16361594200134277s
            emotion time: 0.40578532218933105s
            color map time: 0.03820037841796875s
            enqueue time: 0.040246009826660156s
            Analysis done.
        The music loading takes most of the time
        """
        print("Start analyzing...")

        if os.path.basename(f_path) in self.rgb_cache:
            print("Load from cache...")
            self.rgb_seq = self.rgb_cache[os.path.basename(f_path)]
            self.hsv_seq = self.hsv_cache[os.path.basename(f_path)]
            print("Analysis done.")
            return

        self.rgb_seq = []
        self.hsv_seq = []

        print(f"loading...{os.path.basename(f_path)}")
        y, fs = load_audio(f_path)
        hue_map = np.zeros(math.ceil(len(y)/hop_length))
        saturation_map = np.zeros_like(hue_map)
        value_map = np.zeros_like(hue_map)
        times = librosa.times_like(hue_map, sr=fs, hop_length=hop_length)   # timestamp sequence
        self.sr = fs / hop_length
        print("loading done")

        # ----- tempo and beats ----- #
        onset_env = librosa.onset.onset_strength(y, fs, aggregate=np.median)
        tempo, beats = librosa.beat.beat_track(onset_envelope=onset_env, sr=fs, hop_length=hop_length)
        beat_sequence = np.zeros_like(hue_map)
        # soften beat sequence
        beat_sequence[beats] = 1.0
        beat_gap = 60 / tempo * fs / hop_length
        beat_soft = np.convolve(beat_sequence, np.hamming(2 * beat_gap * 0.4), mode='same')

        # ----- energy ----- #
        energy = librosa.feature.rms(y, frame_length=win_length, hop_length=hop_length)[0]
        energy /= np.max(energy)    # normalize energy

        # ----- emotion ----- #
        # the param of mel is determined by the training of neural net
        mel = librosa.feature.melspectrogram(y=y, sr=fs, n_fft=512, hop_length=256, win_length=512, fmax=8000)
        mel = librosa.power_to_db(mel, ref=np.max)
        emotion = self.emotion_recog(mel, channel=80)

        # ----- color map ----- #
        # hue
        hue_map += energy + 0.6 * beat_soft
        hue_map = np.convolve(hue_map, np.ones(16) / 16, mode='same')  # filter
        hue_map /= np.max(hue_map)
        hue_map = hue_map * 240 + emotion * 90
        # hue_map *= 135 + emotion * 90   # centered at four quadrant, which is determined by the emotion
        hue_map = (hue_map + 360) % 360

        # saturation
        saturation_map += energy + 0.5 * beat_soft
        saturation_map = saturation_map / np.max(saturation_map) * 0.8 + 0.2    # not too unsaturated
        saturation_map = np.convolve(saturation_map, np.ones(32) / 32, mode='same')  # filter

        # value
        value_map += energy + 0.6 * beat_soft
        value_map = value_map / np.max(value_map) * 0.6 + 0.4   # not too dim
        value_map = np.convolve(value_map, np.ones(8) / 8, mode='same')  # filter

        r, g, b = hsv2rgb(hue_map, saturation_map, value_map)

        for R, G, B, H, S, V, t in zip(r, g, b, hue_map, saturation_map, value_map, times):
            self.rgb_seq.append((int(R), int(G), int(B)))
            self.hsv_seq.append((H, S, V))

        print("Analysis done.")

    def get_color(self, music_pos):
        if int(music_pos * self.sr) < len(self.rgb_seq):
            return self.rgb_seq[int(music_pos * self.sr)], \
                   self.hsv_seq[int(music_pos * self.sr)]
        else:
            return (0, 0, 0), (0, 0, 0)

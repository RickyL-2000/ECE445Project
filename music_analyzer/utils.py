import subprocess
import os
import numpy as np
import warnings
import librosa

def exe_cmd(cmd, verbose=True):
    """
    :return: (stdout, stderr=None)
    """
    r = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    ret = r.communicate()
    r.stdout.close()
    if verbose:
        res = str(ret[0].decode()).strip()
        if res:
            print(res)
    if ret[1] is not None:
        print(str(ret[0].decode()).strip())
    return ret

def mkdir(path):
    folder = os.path.exists(path)
    if not folder:
        os.makedirs(path)
    return path

def note2freq(note, a4=440):
    if type(note) is np.ndarray:
        ret = np.zeros(shape=note.shape)
        tmp = a4 * 2 ** ((note - 69) / 12)
        ret[~np.isclose(note, -1)] = tmp[~np.isclose(note, -1)]
        return ret
    if np.isclose(note, -1):
        return 0.0
    return a4 * 2 ** ((note - 69) / 12)

def freq2note(freq, a4=440):
    if type(freq) is np.ndarray:
        ret = -np.ones(shape=freq.shape)
        tmp = np.log2(freq/a4 + 1e-6) * 12 + 69
        ret[~np.isclose(freq, 0.0)] = tmp[~np.isclose(freq, 0.0)]
        return ret
    if np.isclose(freq, 0.0):
        return -1
    return np.log2(freq / a4) * 12 + 69

def load_audio(f_path, fs=22050, filter_warnings=True):
    if not filter_warnings:
        y, fs = librosa.load(f_path, dtype=float, sr=fs)
    else:
        with warnings.catch_warnings():
            warnings.simplefilter('ignore')
            y, fs = librosa.load(f_path, dtype=float, sr=fs)
    if len(y.shape) > 1 and y.shape[0] > 1:     # multi-channel
        y = librosa.to_mono(y)
    return y, fs

def hsv2rgb(h: np.ndarray, s: np.ndarray, v: np.ndarray):
    h60 = h / 60
    h60f = np.floor(h60)
    hi = h60f % 6
    f = h60 - h60f
    p = v * (1 - s)
    q = v * (1 - f * s)
    t = v * (1 - (1 - f) * s)
    r, g, b = np.zeros_like(h), np.zeros_like(h), np.zeros_like(h)
    for i in range(h.shape[0]):
        if hi[i] == 0:
            r[i], g[i], b[i] = v[i], t[i], p[i]
        elif hi[i] == 1:
            r[i], g[i], b[i] = q[i], v[i], p[i]
        elif hi[i] == 2:
            r[i], g[i], b[i] = p[i], v[i], t[i]
        elif hi[i] == 3:
            r[i], g[i], b[i] = p[i], q[i], v[i]
        elif hi[i] == 4:
            r[i], g[i], b[i] = t[i], p[i], v[i]
        elif hi[i] == 5:
            r[i], g[i], b[i] = v[i], p[i], q[i]
    return r*255, g*255, b*255

def output2C(base_dir, length=400):
    R, G, B = [], [], []
    with open(base_dir + '/output.txt') as f:
        fs = float(f.readline().strip())
        for i in range(length):
            r, g, b = f.readline().strip().split()
            R.append(r)
            G.append(g)
            B.append(b)
    outputC = f"unsigned char R[{length}] = {{{', '.join(R)}}};\n" \
              f"unsigned char G[{length}] = {{{', '.join(G)}}};\n" \
              f"unsigned char B[{length}] = {{{', '.join(B)}}};\n"
    with open(base_dir + '/outputC.txt', 'w') as f:
        f.write(outputC)

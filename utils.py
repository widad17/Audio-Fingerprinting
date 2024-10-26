from scipy.ndimage import maximum_filter
import os
import time
import numpy as np
import librosa
from tqdm import tqdm

def print_directory_structure(startpath):
    for root, dirs, files in os.walk(startpath):
        level = root.replace(startpath, '').count(os.sep)
        indent = ' ' * 4 * (level)
        print(f'{indent}{os.path.basename(root)}/')
        subindent = ' ' * 4 * (level + 1)
        for f in files:
            print(f'{subindent}{f}')

def generate_constellation_map(audio_file, n_fft=4096, win_length=4096, hop_length=512):
    try:
        y, sr = librosa.load(audio_file, sr=None)
        S = np.abs(librosa.stft(y, n_fft=n_fft, win_length=win_length, hop_length=hop_length))
        S_db = np.log(S)
        S_db = S_db[:1024, :]
        
        neighbourhood_size = 31
        peaks = []

        maximum_filter_output = maximum_filter(S_db, size=neighbourhood_size)
        is_peak = maximum_filter_output == S_db

        peaks = np.argwhere(is_peak)

        return peaks.tolist(), sr
    except Exception as e:
        print(f"Error processing {audio_file}: {str(e)}")
        return None, None


def target_zone(anchor, peaks, time_offset, time_width, freq_width):
        """
        An iterator through that iterates through the peaks in the target zone
        """
        # Note that the anchor is a tuple of (f, t)
        f, t = anchor
        time_min = t + time_offset
        time_max = t + time_offset + time_width
        freq_min = f - int(freq_width / 2)
        freq_max = freq_min + freq_width

        for peak in peaks:
            if peak[1] < time_min or peak[1] > time_max:
                continue
            if peak[0] < freq_min or peak[0] > freq_max:
                continue

            yield peak  


def generate_hashes(constellation):
    hashes = []

    for i in tqdm(range(len(constellation)), desc='Computing hashes'):
        anchor_peak = constellation[i]
        for other_peak in target_zone(anchor_peak, constellation, 1, 100, 300):
            # Create hash
            # Note that each peak is on the form (f, t)
            hash_value = hash((anchor_peak[0], other_peak[0], other_peak[1] - anchor_peak[1]))
            hashes.append((hash_value, anchor_peak[1]))

    return hashes

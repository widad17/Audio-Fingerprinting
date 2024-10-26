import os 
import argparse
import librosa
import numpy as np
import soundfile as sf
from tqdm import tqdm
from pydub import AudioSegment

parser = argparse.ArgumentParser('Create test queries')

parser.add_argument('-s', '--source', required=True, help='The training data folder')
parser.add_argument('-d', '--dest', required=True, help='The queries folder')
parser.add_argument('-n', '--noise', required=False, help='The standard deviation of a gaussian noise')

args = parser.parse_args()

if not os.path.isdir(args.source):
    raise Exception('source must be a valid folder')

if not os.path.isdir(args.dest):
    raise Exception('dest must be a directory')


for root, dirs, files in tqdm(os.walk(args.source), desc='Creating samples'):
    for name in files:
        if name.endswith('.mp3') or name.endswith('.wav'):
            waveform, sr = librosa.load(os.path.join(root, name), sr=None)
            # frames in 10 seconds
            nr_frames = sr * 10

            # A random portion:
            start = np.random.randint(0, len(waveform) - nr_frames)
            end = start + nr_frames

            sample_waveform = waveform[start:end]

            if args.noise is not None:
                sample_waveform = sample_waveform + np.random.normal(loc=0, scale=float(args.noise), size=len(sample_waveform))

            clean_name = name.split('.')[0]

            new_path = os.path.join(args.dest, f'{clean_name}.mp3')

            audio_segment = AudioSegment(
                sample_waveform.tobytes(),
                frame_rate=sr,
                sample_width=sample_waveform.dtype.itemsize,
                channels=1  # Assuming mono audio. For stereo, you can adjust this.
            )

            sf.write(new_path, sample_waveform, sr)
import os
import time
import numpy as np
import librosa
from collections import defaultdict

def print_directory_structure(startpath):
    for root, dirs, files in os.walk(startpath):
        level = root.replace(startpath, '').count(os.sep)
        indent = ' ' * 4 * (level)
        print(f'{indent}{os.path.basename(root)}/')
        subindent = ' ' * 4 * (level + 1)
        for f in files:
            print(f'{subindent}{f}')

def generate_constellation_map(audio_file, n_fft=4096, hop_length=512):
    try:
        y, sr = librosa.load(audio_file)
        S = np.abs(librosa.stft(y, n_fft=n_fft, hop_length=hop_length))
        S_db = librosa.amplitude_to_db(S, ref=np.max)
        
        constellation = []
        for freq_bin in range(S_db.shape[0]):
            peaks = librosa.util.peak_pick(S_db[freq_bin], pre_max=30, post_max=30, pre_avg=30, post_avg=30, delta=0.5, wait=10)
            for peak in peaks:
                constellation.append((peak, freq_bin))
        
        print(f"Generated {len(constellation)} peaks for {audio_file}")
        return constellation, sr
    except Exception as e:
        print(f"Error processing {audio_file}: {str(e)}")
        return None, None

def generate_hashes(constellation, fan_out=15, d_time=200):
    hashes = []
    for i, anchor in enumerate(constellation):
        for j in range(i + 1, min(i + fan_out, len(constellation))):
            point = constellation[j]
            t1, f1 = anchor
            t2, f2 = point
            if 0 < t2 - t1 <= d_time:
                hash_value = hash((f1, f2, t2 - t1))
                hashes.append((hash_value, t1))
    print(f"Generated {len(hashes)} hashes from {len(constellation)} peaks")
    return hashes

class ShazamDatabase:
    def __init__(self):
        self.db = defaultdict(list)
    
    def add_song(self, song_id, hashes):
        for hash_value, t in hashes:
            self.db[hash_value].append((song_id, t))
        print(f"Added {len(hashes)} hashes for {song_id}")
    
    def search(self, sample_hashes):
        matches = defaultdict(list)
        for hash_value, sample_t in sample_hashes:
            if hash_value in self.db:
                for song_id, db_t in self.db[hash_value]:
                    matches[song_id].append((db_t, sample_t))
        print(f"Found matches in {len(matches)} songs")
        return matches

    def get_total_hashes(self):
        return sum(len(v) for v in self.db.values())

def build_database(train_folder):
    db = ShazamDatabase()
    if not os.path.exists(train_folder):
        print(f"Error: The folder '{train_folder}' does not exist.")
        return db

    print(f"Contents of '{train_folder}':")
    print_directory_structure(train_folder)

    total_files = sum([len([f for f in files if f.endswith('.mp3')]) for r, d, files in os.walk(train_folder)])
    processed_files = 0

    for subdir in os.listdir(train_folder):
        subdir_path = os.path.join(train_folder, subdir)
        if os.path.isdir(subdir_path):
            for file in os.listdir(subdir_path):
                if file.endswith('.mp3'):
                    audio_file = os.path.join(subdir_path, file)
                    song_id = f"{subdir}_{file}"
                    constellation, sr = generate_constellation_map(audio_file)
                    if constellation is not None:
                        hashes = generate_hashes(constellation)
                        db.add_song(song_id, hashes)
                        processed_files += 1
                        print(f"Added to database: {song_id} ({processed_files}/{total_files})")

    print(f"Total hashes in database: {db.get_total_hashes()}")
    return db

def identify_song(db, query_file, top_n=5):
    try:
        constellation, _ = generate_constellation_map(query_file)
        if constellation is None:
            return None
        sample_hashes = generate_hashes(constellation)
        matches = db.search(sample_hashes)
        top_matches = find_top_matches(matches, top_n)
        return top_matches
    except Exception as e:
        print(f"Error processing query file {query_file}: {str(e)}")
        return None

def find_top_matches(matches, top_n=5):
    scores = defaultdict(int)
    for song_id, time_pairs in matches.items():
        hist = defaultdict(int)
        for db_t, sample_t in time_pairs:
            hist[db_t - sample_t] += 1
        scores[song_id] = max(hist.values()) if hist else 0
    return sorted(scores.items(), key=lambda x: x[1], reverse=True)[:top_n]

if __name__ == "__main__":
    train_folder = "kikibouba_train"
    print("Building database...")
    db = build_database(train_folder)
    print("Database built.")
    
    query_folder = "queries"
    min_score_threshold = 100  # Adjusted threshold
    
    print("\nProcessing queries...")
    for query_file in os.listdir(query_folder):
        if query_file.endswith('.wav'):
            query_path = os.path.join(query_folder, query_file)
            time_1 = time.time()
            top_matches = identify_song(db, query_path)
            time_2 = time.time()
            print(f"It took {time_2 - time_1} seconds to identify the top matches")
            print(f"\nQuery: {query_file}")
            if top_matches:
                for i, (match, score) in enumerate(top_matches, 1):
                    print(f"Match {i}: {match} (Score: {score})")
                    if i == 1 and score >= min_score_threshold:
                        print("Reliable match found")
                    elif i == 1:
                        print("Match found, but below threshold")
            else:
                print("No matches found")
            print("---")

    print("\nPerformance Analysis:")
    print(f"Minimum score threshold: {min_score_threshold}")
   
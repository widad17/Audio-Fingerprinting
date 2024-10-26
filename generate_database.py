import os

import settings
from database_classes import ShazamDatabaseSql
from utils import generate_constellation_map, generate_hashes, print_directory_structure


def build_database(train_folder, n_fftS, win_lengthS, hop_lengthS):
    db = ShazamDatabaseSql()
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
                    db.add_song(song_id)
                    for LOD in range(3):
                        constellation, sr = generate_constellation_map(audio_file,
                                                                       n_fftS[LOD],
                                                                       win_lengthS[LOD],
                                                                       hop_lengthS[LOD])

                        if constellation is not None:
                            hashes = generate_hashes(constellation)
                            db.add_hashes(song_id, hashes, LOD)
                            processed_files += 1
                            print(f"Added to database: {song_id} ({processed_files}/{total_files * 3})")

    print(f"Total hashes in database: {db.get_total_hashes(0) + db.get_total_hashes(1) + db.get_total_hashes(2)}")
    return db


if __name__ == "__main__":
    train_folder = "covers80/covers32k"
    # we should probably need to add here more folders, or create a huge folder with all songs we want
    # to be collected in our database
    print("Building database...")
    lod_params = settings.LOD_PARAMS
    db = build_database(train_folder, lod_params['nffts'], lod_params['win_lengths'], lod_params['hop_lengths'])
    print("Database built.")
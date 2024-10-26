import os
from pathlib import Path
import time
import settings
import numpy as np
from database_classes import ShazamDatabaseSql
from searching_utils import LOD_search, identify_song


if __name__ == "__main__":
    db = ShazamDatabaseSql()

    query_folder = "kikibouba_samples"
    min_score_threshold = 100  # Adjusted threshold

    n_queries = len([f for f in Path(query_folder).iterdir() if f.is_file()])

    higher_level_search_times = np.zeros(n_queries)
    LOD_search_times = np.zeros(n_queries)

    """
    Need to predefine here the n_fftS, win_lengthS and hop_lengthS used for queries,
    that should be the same used for the database
    """
    
    print("\nProcessing queries...")
    for j,query_file in enumerate(os.listdir(query_folder)):
        if query_file.endswith('.mp3'):
            query_path = os.path.join(query_folder, query_file)
            lod_params = settings.LOD_PARAMS


            # Compute and track time for fixed highest LOD identification
            time_1 = time.time()
            top_matches_fixed = identify_song(db,
                                              query_path,
                                              lod_params['nffts'],
                                              lod_params['win_lengths'],
                                              lod_params['hop_lengths'],
                                              None
                                              # add n_fftS and all arguments
                                              )
            time_2 = time.time()
            higher_level_search_times[j] = time_2 - time_1

            # Compute and track time for iterative LOD search identification
            time_1_LOD = time.time()
            top_matches_LOD = LOD_search(db,
                                              query_path,
                                              lod_params['nffts'],
                                              lod_params['win_lengths'],
                                              lod_params['hop_lengths'],
                                              None
                                              # add n_fftS and all arguments
                                              )
            time_2_LOD = time.time()
            LOD_search_times[j] = time_2_LOD - time_1_LOD

            print(f"\nQuery: {query_file}")
            if top_matches_fixed:
                for i, (match, score) in enumerate(top_matches_fixed, 1):
                    print(f"Match {i}: {match} (Score: {score})")
                    if i == 1 and score >= min_score_threshold:
                        print("Reliable match found")
                    elif i == 1:
                        print("Match found, but below threshold")
            else:
                print("No matches found")
            print("---")
            print(f"\nQuery: {query_file}")
            if top_matches_LOD:
                for i, (match, score) in enumerate(top_matches_LOD, 1):
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
    print(f"Direct research in higher LOD times statistics: {np.mean(higher_level_search_times)} mean, {np.var(higher_level_search_times)} variance")
    print(f"Iterative LOD search times statistics: {np.mean(LOD_search_times)} mean, {np.var(LOD_search_times)} variance")
    db.close()
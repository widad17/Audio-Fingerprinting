from collections import defaultdict
from utils import generate_constellation_map, generate_hashes


def identify_song(db, query_file, n_fftS, win_lengthS, hop_lengthS, previous_matches, LOD = 2, top_n = 5):
    """
    search for the query through a fixed LOD in the database

    Parameters:
        - n_fftS, win_lengthS, hop_lengthS: lists of the sizes for each parameter for each level of detail.
            (ie, n_fftS[0] corresponds to n_fft used for STFT at LOD 0)
        - previous_matches : list of songs that has to be used for the next LOD comparison
        - LOD : LOD that increases at each iteration
        - top_n : number of songs with matches used for next level (maybe need to change this, or use higher values,
            decrease it at each iteration)

    Returns:
    list: best matches.
    """

    try:
        n_fft,win_length,hop_length = n_fftS[LOD], win_lengthS[LOD], hop_lengthS[LOD]
        constellation, _ = generate_constellation_map(query_file,n_fft,win_length,hop_length)
        if constellation is None:
            return None
        sample_hashes = generate_hashes(constellation)
        matches = db.search(sample_hashes, LOD)
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


def LOD_search(db, query_file, n_fftS, win_lengthS, hop_lengthS, previous_matches, LOD = 0, top_n = 30):
    """
    iterative LOD search trough the database

    Parameters:
        - n_fftS, win_lengthS, hop_lengthS: lists of the sizes for each parameter for each level of detail.
            (ie, n_fftS[0] corresponds to n_fft used for STFT at LOD 0)
        - previous_matches : list of songs that has to be used for the next LOD comparison
        - LOD : LOD that increases at each iteration
        - top_n : number of songs with matches used for next level (maybe need to change this, or use higher values,
            decrease it at each iteration)

    Returns:
    list: best matches.
    """
    try:
        constellation, _ = generate_constellation_map(query_file,
                                                        n_fft=n_fftS[LOD],
                                                        win_length=win_lengthS[LOD],
                                                        hop_length=hop_lengthS[LOD])
        if constellation is None:
            return None
        sample_hashes = generate_hashes(constellation)
        matches = db.search(sample_hashes, LOD)#, previous_matches)

        if previous_matches is not None:
            matches = {key: matches[key] for key in previous_matches if key in matches}   ## we are lacking a way to filter just trough hashes that appear in the matches found in previous LOD (for lowest LOD, use all hashes)

        top_matches = find_top_matches(matches, top_n)

        if LOD < 2:
            previous_matches_song_id = list(set([x[0] for x in top_matches]))

            return LOD_search(db,
                              query_file,
                              n_fftS,
                              win_lengthS,
                              hop_lengthS,
                              previous_matches=previous_matches_song_id,
                              LOD = LOD + 1,
                              top_n = 15 if LOD == 0 else 5)
        else: 
            return top_matches
    except Exception as e:
        print(f"Error processing query file {query_file}: {str(e)}")
        return None
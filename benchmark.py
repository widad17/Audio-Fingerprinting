import argparse
import os
import librosa
from search_through import LOD_search
from database_classes import ShazamDatabaseSql
import time
import settings

parser = argparse.ArgumentParser()

parser.add_argument('-s', '--source', required=True, help='The sample folder')

args = parser.parse_args()

db = ShazamDatabaseSql()

nr_of_queries = len(os.listdir(args.source))
nr_of_correct_queries = 0

lod_params = settings.LOD_PARAMS

start_time = time.time()

for file in os.listdir(args.source):
    top_songs = LOD_search(
        db, 
        os.path.join(args.source, file),
        lod_params['nffts'],
        lod_params['win_lengths'],
        lod_params['hop_lengths'],
        None
        )
    if len(top_songs) > 0 and file in top_songs[0][0]:
        nr_of_correct_queries += 1
    else:
        print (file)
        print (top_songs)

end_time = time.time()

print (f'Total number of queries: {nr_of_queries}')
print (f'Nr of correct queries: {nr_of_correct_queries}')
print (f'Accuracy: {(nr_of_correct_queries / nr_of_queries) * 100}')
print (f'This took {end_time - start_time} seconds')
print (f'{(end_time - start_time) / nr_of_queries} seconds per query')
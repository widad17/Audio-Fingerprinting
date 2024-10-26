from collections import defaultdict
import os
import sqlite3
import settings


class ShazamDatabaseSql:
    def __init__(self):
        self.conn = sqlite3.connect(os.path.join(settings.DATABASE_PATH, settings.DATABASE_NAME))
        self.cur = self.conn.cursor()

    def add_song(self, song_id):
        self.cur.execute('INSERT INTO songs VALUES (?, ?)', (song_id, song_id))
        self.conn.commit()


    def add_hashes(self, song_id, hashes, LOD):
        for hash_value, t in hashes:
            self.cur.execute(f'INSERT INTO song_hashes_{LOD} VALUES (?, ?, ?)', (song_id, hash_value, t))

        print(f"Added {len(hashes)} hashes for {song_id}")


    def get_songs_by_hash(self, hash_value, LOD, restricted_songs = None):
        if restricted_songs is None:
            res = self.cur.execute(
                f'SELECT song_id, time_stamp FROM song_hashes_{LOD} WHERE hash_value = ?',
                (hash_value,))
        else:
            res = self.cur.execute(
                f'SELECT song_id, time_stamp FROM song_hashes_{LOD} WHERE song_id IN ? AND hash_value = ?',
                (restricted_songs, hash_value))
        return res.fetchall()


    def search(self, sample_hashes,LOD,restricted_songs=None):
        matches = defaultdict(list)
        for hash_value, sample_t in sample_hashes:
            database_hashes = self.get_songs_by_hash(hash_value, LOD, restricted_songs)
            for song_id, db_t in database_hashes:
                matches[song_id].append((db_t, sample_t))
       
        print(f"Found matches in {len(matches)} songs")
        return matches


    def get_total_hashes(self, LOD):
        res = self.cur.execute(f'SELECT count(*) from song_hashes_{LOD}')
        return res.fetchone()[0]
    
    def close(self):
        self.conn.close()

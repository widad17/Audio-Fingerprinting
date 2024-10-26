CREATE TABLE songs (
    song_id VARCHAR(255) PRIMARY KEY,
    title VARCHAR(255)
);

CREATE TABLE song_hashes_0 (
    song_id VARCHAR(255) references songs(database_file),
    hash_value int,
    time_stamp int
);

CREATE TABLE song_hashes_1 (
    song_id VARCHAR(255) references songs(database_file),
    hash_value int,
    time_stamp int
);

CREATE TABLE song_hashes_2 (
    song_id VARCHAR(255) references songs(database_file),
    hash_value int,
    time_stamp int
);


CREATE INDEX hash_index_0 ON song_hashes_0(hash_value);
CREATE INDEX hash_index_1 ON song_hashes_1(hash_value);
CREATE INDEX hash_index_2 ON song_hashes_2(hash_value);

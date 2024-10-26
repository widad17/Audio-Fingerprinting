DATABASE_PATH = './database'
DATABASE_NAME = 'covers.db'

LOD_PARAMS = {
    'nffts': [2**14, 2**13, 2**12],
    'win_lengths': [2**14, 2**13, 2**12],
    'hop_lengths': [int(2**14 / 2), int(2**13 / 2), int(2**12 / 2)],
}
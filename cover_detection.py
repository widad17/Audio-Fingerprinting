from collections import defaultdict
import os
from pathlib import Path
import time

import numpy as np
from database_classes import ShazamDatabaseSql
from utils import generate_constellation_map, generate_hashes


if __name__ == "__main__":
    db = ShazamDatabaseSql()

    """
    I would do 2 tests : 
        - try computing one cover that is not in the database, 
        but with another version of the same song being in it, and seeing if it might actually track at least song.

        - having both versions of a song, looking if there is a clear difference in between
        scores obtained for the 2 versions when looking for the actual cover
    """

    

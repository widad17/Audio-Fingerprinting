import os
import argparse

parser = argparse.ArgumentParser()

parser.add_argument('-n', '--name')

args = parser.parse_args()
database_path = os.path.join('./database', args.name)
init_path = os.path.join('./database', 'init.sql')

os.system(f'sqlite3 {database_path} <  {init_path}')
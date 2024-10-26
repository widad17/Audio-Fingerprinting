import os

COVERS_80_DIR = 'covers80\\covers32k'

#print (os.listdir(COVERS_80_DIR))

for dir in os.listdir(COVERS_80_DIR):
    #print (os.listdir(os.path.join(COVERS_80_DIR, dir)))
    if os.path.isdir(os.path.join(COVERS_80_DIR, dir)) and len(os.listdir(os.path.join(COVERS_80_DIR, dir))) > 2:
        print (dir)


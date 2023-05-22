import os

files = []

for filename in os.listdir("./Backgrounds"):

    if filename.endswith("PNG"):

        files.append(filename[:-4])

# Auxiliary script that exports the absolute paths of all files in the current directory into the 'train_images.txt' file. This file is then used by some models during training or validation to find their respective datasets.

import os

train_dir = os.path.dirname(os.path.abspath(__file__))
file_list = os.listdir(train_dir)

with open('train_images.txt', 'w') as f:
    for file_name in file_list:
        f.write(os.path.abspath(os.path.join(train_dir, file_name)) + '\n')
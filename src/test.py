import numpy as np
import matplotlib.pyplot as plt
import PIL.Image
import pyspng
# import os

# path='..\\..\\img\\training_imgs\\urban_classifier\\extracted\\fill_pct_20\\north_0_1_20.png'
path='../../img/training_imgs/urban_classifier/extracted2/south_29_4_90.png'
# path='../..\\img/training_imgs/urban_classifier\\extracted/test.png'

print("123")
path = open(path, "rb")

# image = np.array(PIL.Image.open(path))
image = pyspng.load(path.read())
print(image.shape)
print("456")
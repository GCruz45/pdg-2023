import numpy as np
import matplotlib.pyplot as plt
import pandas as pd

import cv2
from skimage.restoration import inpaint

from PIL import Image

import sys
import subprocess


class SatImgDownloader:
	def __init__(self, img_source):
		self.img_source = img_source
	
	def inpaint(self, distort_img, mask):
		if self.algorithm == "ns":
			result = cv2.inpaint(distort_img, mask, 3, cv2.INPAINT_NS) 
		elif self.algorithm == "telea":
			result = cv2.inpaint(distort_img, mask, 3, cv2.INPAINT_TELEA) 
		elif self.algorithm == "biharmonic":
			result = inpaint.inpaint_biharmonic(distort_img, mask)
		return result

# algo = sys.argv[1]
# inpainter = basicInpainting(algo)
#
# img_path = "./" + sys.argv[2]
# img = cv2.imread(img_path)
# img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
# mask_path = "./" + sys.argv[3]
# mask = cv2.imread(mask_path)
# mask = cv2.cvtColor(mask, cv2.COLOR_BGR2GRAY)
#
# result = inpainter.inpaint(img, mask)
#
# #printImg(result)
# #plt.figure(figsize=(15, 20))
# #plt.imshow(result)
# #result.show()
# result = Image.fromarray(result)
# imgName = "inpainted-" + algo + ".png"
# result.save(imgName)
# #Image.save(Image.fromarray(result)
# subprocess.call([imgName], shell=True)

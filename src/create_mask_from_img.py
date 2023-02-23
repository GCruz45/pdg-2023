
import tensorflow as tf

import numpy as np
import matplotlib.pyplot as plt
import pandas as pd

import cv2
from skimage.restoration import inpaint

from PIL import Image

import sys
import subprocess

from skimage import data


class BasicInpainting:

    def __init__(self, algorithm, rgb_img_with_holes, mask):
        self.algorithm = algorithm
        self.mask = mask
        self.rgb_img_with_holes = rgb_img_with_holes

    def convert_mask_to_zeros_and_ones(self, old_mask):
        return np.where((old_mask > 0), 1, 0).astype('bool')

    def inpaint(self):

        result = 0 * self.rgb_img_with_holes  # Initialize output.

        # =============================================================================
        #     Basic checks
        # =============================================================================
        if len(self.rgb_img_with_holes.shape) != 3:
            print(self.rgb_img_with_holes.shape)
            print('The inpainting methods in this section only work with 3-channel color images !!.')
            return result

        if self.rgb_img_with_holes.shape[2] != 3:
            print('The inpainting methods in this section only work with 3-channel color images !!.')
            return result

        if self.algorithm == "ns":
            result = cv2.inpaint(self.rgb_img_with_holes, self.mask, 3, cv2.INPAINT_NS)
        elif self.algorithm == "telea":
            result = cv2.inpaint(self.rgb_img_with_holes, self.mask, 3, cv2.INPAINT_TELEA)
        elif self.algorithm == "biharmonic":
            # Convert mask to boolean
            self.mask = self.convert_mask_to_zeros_and_ones(self.mask)

            # Create an rgb img with holes from an unaltered img
            defective_img = self.rgb_img_with_holes * ~self.mask[..., np.newaxis]

            result = inpaint.inpaint_biharmonic(defective_img, self.mask, channel_axis=-1)
        return result

    def print_img(self, image):
        # %matplotlib inline

        # image = cv2.imread(path)
        height, width = image.shape[:2]
        resized_image = cv2.resize(image, (3 * width, 3 * height), interpolation=cv2.INTER_CUBIC)

        fig = plt.gcf()
        fig.set_size_inches(18, 10)
        plt.axis("off")
        plt.imshow(cv2.cvtColor(resized_image, cv2.COLOR_BGR2RGB))
        plt.show()


def run():
    print("\n~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~\n")
    # Example of usage: python create_mask_from_img.py usgs_img/LE70090582007029EDC00/L71009058_05820070129_B123.tif

    img_folder_path = "../../img/"
    img_path = img_folder_path + sys.argv[1]
    mask_path = img_folder_path + "masked_img/converted_mask.tif" 

    pil_img = Image.open(img_path)
    np_img = np.array(pil_img) 


    
    mask_pil_img = Image.fromarray(np_img)


    pil_inpainted_img = Image.fromarray((255 * inpainted_img).astype('uint8'))
    # pil_inpainted_img = Image.fromarray(inpainted_img.astype('uint8'))
    pil_inpainted_img.show()
    inpainted_img_name = "inpainted-" + algo + ".png"
    inpainted_img_path = img_folder_path + "/inpainted_img/" + inpainted_img_name
    pil_inpainted_img.save(inpainted_img_path)
    # Image.save(Image.fromarray(inpainted_img)
    # subprocess.call([inpainted_img_path], shell=True)


run()

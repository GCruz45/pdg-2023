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
        return np.where((old_mask > 0), 1, 0).astype("bool")

    def inpaint(self):

        result = 0 * self.rgb_img_with_holes  # Initialize output.

        # =============================================================================
        #     Basic checks
        # =============================================================================
        if len(self.rgb_img_with_holes.shape) != 3:
            print(self.rgb_img_with_holes.shape)
            print(
                "The inpainting methods in this section only work with 3-channel color images !!."
            )
            return result

        if self.rgb_img_with_holes.shape[2] != 3:
            print(
                "The inpainting methods in this section only work with 3-channel color images !!."
            )
            return result

        if self.algorithm == "ns":
            result = cv2.inpaint(self.rgb_img_with_holes, self.mask, 3, cv2.INPAINT_NS)
        elif self.algorithm == "telea":
            result = cv2.inpaint(
                self.rgb_img_with_holes, self.mask, 3, cv2.INPAINT_TELEA
            )
        elif self.algorithm == "biharmonic":
            # Convert mask to boolean
            self.mask = self.convert_mask_to_zeros_and_ones(self.mask)

            # Create an rgb img with holes from an unaltered img
            defective_img = self.rgb_img_with_holes * ~self.mask[..., np.newaxis]

            result = inpaint.inpaint_biharmonic(
                defective_img, self.mask, channel_axis=-1
            )
        return result

    def print_img(self, image):
        # %matplotlib inline

        # image = cv2.imread(path)
        height, width = image.shape[:2]
        resized_image = cv2.resize(
            image, (3 * width, 3 * height), interpolation=cv2.INTER_CUBIC
        )

        fig = plt.gcf()
        fig.set_size_inches(18, 10)
        plt.axis("off")
        plt.imshow(cv2.cvtColor(resized_image, cv2.COLOR_BGR2RGB))
        plt.show()


def run():
    print("\n~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~\n")
    # Example of usage: python basic_inpainting.py biharmonic maskRGB2.png bw-mask.png

    tf.random.set_seed(seed=1322)

    algo = sys.argv[1]
    input_img_name = sys.argv[2]
    input_mask_name = sys.argv[3]

    img_folder_path = "../../img/inpainted_imgs"
    img_path = img_folder_path + "/input/" + input_img_name
    mask_path = img_folder_path + "/mask/" + input_mask_name

    outer_img = cv2.imread(img_path)
    outer_img = cv2.cvtColor(outer_img, cv2.COLOR_BGR2RGB)

    ##### DEBUG #######
    # mask = np.zeros(outer_img.shape[:-1], dtype=bool)
    # print("MASK SHAPE: {0}".format(mask.shape))
    # image_orig = data.astronaut()
    # print("local img shape: {0}, astronaut img shape: {1}".format(outer_img.shape, image_orig.shape))
    # print("local img dtype: {0}, astronaut img dtype: {1}".format(outer_img[0].dtype, image_orig[0].dtype))
    ###################

    outer_mask = cv2.imread(mask_path)
    outer_mask = cv2.cvtColor(outer_mask, cv2.COLOR_BGR2GRAY)

    inpainter = BasicInpainting(algo, outer_img, outer_mask)
    inpainted_img = inpainter.inpaint()

    # plt.imshow(inpainted_img)
    # plt.show()

    pil_inpainted_img = Image.fromarray(inpainted_img.astype("uint8"))
    if algo == "biharmonic":
        pil_inpainted_img = Image.fromarray((255 * inpainted_img).astype("uint8"))

    pil_inpainted_img.show()
    inpainted_img_name = "inpainted_" + algo + "_" + input_img_name
    inpainted_img_path = img_folder_path + "/result/" + inpainted_img_name
    pil_inpainted_img.save(inpainted_img_path)
    # Image.save(Image.fromarray(inpainted_img)
    # subprocess.call([inpainted_img_path], shell=True)


run()

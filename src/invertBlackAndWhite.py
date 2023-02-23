import numpy as np
import cv2
import json
from matplotlib import pyplot as plt
from PIL import Image


def read_this(image_file, gray_scale=False):
    image_src = cv2.imread(image_file)
    if gray_scale:
        image_src = cv2.cvtColor(image_src, cv2.COLOR_BGR2GRAY)
    else:
        image_src = cv2.cvtColor(image_src, cv2.COLOR_BGR2RGB)
    return image_src


def invert_this(image_file, with_plot=False, gray_scale=False):
    image_src = read_this(image_file=image_file, gray_scale=gray_scale)
    # image_i = ~ image_src
    image_i = 255 - image_src

    if with_plot:
        cmap_val = None if not gray_scale else "gray"
        fig, (ax1, ax2) = plt.subplots(nrows=1, ncols=2, figsize=(10, 20))

        ax1.axis("off")
        ax1.title.set_text("Original")

        ax2.axis("off")
        ax2.title.set_text("Inverted")

        ax1.imshow(image_src, cmap=cmap_val)
        ax2.imshow(image_i, cmap=cmap_val)
        return True
    return image_i


# img = cv2.imread("512mask.png")
# img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
img = invert_this(image_file="sample2mask.png", gray_scale=True)
# img = Image.fromarray(img.astype("uint8"))
img = Image.fromarray(img)
img.show()
img.save("sample2maskinverted.png")

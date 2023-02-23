# =============================================================================
#  RGB into BW mask converter
#  Description: Converts an RGB image with a red mask into a black and white
#               mask that converts the red region into white.
#  Usage: import module and call the method
#    Example: python create_mask_from_img.py ../../img/usgs_img/LE70090582007029EDC00/create_mask_from_redFill.tif
# =============================================================================

from PIL import Image
import cv2
import numpy as np
import os

def return_converted_mask(path_to_red_mask, red_mask_file_name):
    # Separate RGB arrays
    #scriptDir = os.path.dirname(__file__)
    #img_path = os.path.join(scriptDir, path_to_red_mask)
    img_path = os.path.join(path_to_red_mask, red_mask_file_name + ".tif")
    im = Image.open(img_path)
    rr, g, b = im.convert('RGB').split()
    r = rr.load() # Allows pixel manipulation for the channel.
    g = g.load()
    b = b.load()
    w, h = im.size

    # Convert non-red pixels to black
    for i in range(w):
        for j in range(h):
            if (r[i, j] != 255 or g[i, j] != 0 or b[i, j] != 0):
                r[i, j] = 0  # Just change R channel

    #thresh = 255
    #fn = lambda x: 0 if x < thresh else 255
    #r = im.convert('L').point(fn, mode='1') # L: (8-bit pixels, black and white); 1: (1-bit pixels, black and white, stored with one pixel per byte)
    rr.save(path_to_red_mask + "bw-mask_of_" + red_mask_file_name + ".png")
    # Merge just the R channel as all channels
    #im = Image.merge('L', r)
    #im = r

    #temp = cv2.resize(im, (w, h), interpolation=cv2.INTER_LINEAR)
    #output = cv2.resize(temp, (w, h), interpolation=cv2.INTER_NEAREST)
    #cv2.imwrite("bw-mask_of_" + rgb_mask_file_name, output)
    #im.save("bw-mask_of_" + rgb_mask_file_name)

    # to expand dims from (m,n) to (m,n,1):
	# y = np.expand_dims(img1, axis=-1) y is the new np array and img1 has m,n dimensions.

return_converted_mask(r"../../img/inpainting_imgs/input/", "cropped-redmask-123")

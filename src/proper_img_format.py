# =============================================================================
#  Properly format image files into given format.
#  Description:     TODO
#  System Args:     [1] File format extension (i.e png).
#                   [2] Planet TM quota period.
#                   [3] Threshold of desired density of target class.

#  Sample usage:    cd C:\Users\gabri\aOneDrive\PDG\gdrive\repo\src
#                   python proper_img_format.py \
#                   5 1 80
#                   # Parameters: [subimages per image, target class, threshold percentage]
# =============================================================================

import sys
import os
import glob
import rasterio
from PIL import Image


def main():
    print("\n@START ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~\n")
    global img_input_directory_rgb
    global img_input_directory_ghs
    global img_output_directory_rgb
    global img_output_directory_ghs
    global format_target_extension
    global threshold
    global region_name
    global img_number
    global aborted_imgs
    format_target_extension = sys.argv[1]
    planet_month_quota = sys.argv[2]
    threshold = int(sys.argv[3])

    img_input_directory_rgb = (
        os.getenv("PDG_IMG_RAW") + "/raw/planet/quota" + planet_month_quota + "/"
    )
    img_input_directory_ghs = os.getenv("PDG_IMG_RAW") + "/raw/ghs/"

    img_output_directory_rgb = (
        os.getenv("PDG_IMG")
        + "/training/quota"
        + planet_month_quota
        + "/fill_pct_"
        + str(threshold)
        + "/"
    )
    img_output_directory_ghs = (
        os.getenv("PDG_IMG")
        + "/ghs/"
        + planet_month_quota
        + "/fill_pct_"
        + str(threshold)
        + "/"
    )

    print("\nSearching image in path: {}\n".format(img_input_directory_rgb))

    # Iterates over each image in the directory
    img_number = 0
    for input_img_path in glob.glob(
        img_input_directory_rgb + "/*." + format_target_extension
    ):
        rgb_output_path = (
            img_output_directory_rgb + str(img_number) + "_" + str(threshold) + ".png"
        )

        img = rasterio.open(input_img_path)
        img_read = img.read()

        with rasterio.open(
            rgb_output_path,
            "w",
            driver="PNG",
            height=512,
            width=512,
            count=3,
            dtype=rasterio.uint8,
        ) as dst:
            dst.write(img_read)
        img_number += 1

    img_number = 0
    for input_img_path in glob.glob(
        img_input_directory_ghs + "/*." + format_target_extension
    ):
        dhs_output_path = (
            img_output_directory_ghs + str(img_number) + "_" + str(threshold) + ".png"
        )

        img = rasterio.open(input_img_path)
        img_read = img.read()

        with rasterio.open(
            dhs_output_path,
            "w",
            driver="PNG",
            height=512,
            width=512,
            count=3,
            dtype=rasterio.uint8,
        ) as dst:
            dst.write(img_read)

        img_number += 1

    print("\n@END ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~\n")


if __name__ == "__main__":
    main()

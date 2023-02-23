# =============================================================================
#  Generate 512x512 crops of rgb and greyscale tiffs of nxm dims.
#  Description:     TODO
#  System Args:     [1] Planet quota number.
#                   [2] Number of images to generate.
#                   [3] Target class (1 = urban, 0 = non-urban).
#                   [4] Threshold of desired density of target class.
#  Sample usage 2:  cd %PDG_REPO% && cd src
#                   python crop_raw_img.py 2 5 1 80 # quota number (i.e 1), subimages per image, target class (1 = urban, 0 = non-urban), threshold percentage (0-100)
# =============================================================================

# To change image bitdepth, try:
# https://rasterio.readthedocs.io/en/latest/topics/writing.html


import sys
import os
import numpy as np
import rasterio
from rasterio.windows import Window
from rasterio.warp import reproject, Resampling


class CropRawImg:
    def __init__(
        self, rgb_img_path, ghs_built_s_img_path, masks_num, target_class, threshold
    ):
        self.rgb_img_path = rgb_img_path
        self.ghs_built_s_img_path = ghs_built_s_img_path
        self.masks_num = int(masks_num)
        self.target_class = int(target_class)
        self.threshold = threshold

    def gen_masks(self):
        print("\nProcessing image #", img_number, "...")
        # Convert rgb tiff to np array
        print(
            "\nImg paths: \n", self.rgb_img_path, "\n", self.ghs_built_s_img_path, "\n"
        )
        rgb_raster_ds = rasterio.open(self.rgb_img_path)
        ghs_raster_ds = rasterio.open(self.ghs_built_s_img_path)

        # Change the crs of the ghs tif to the crs used by the rgb tif
        kwargs = ghs_raster_ds.meta.copy()
        kwargs.update(
            {
                "crs": rgb_raster_ds.crs,
                "transform": rgb_raster_ds.transform,
                "width": rgb_raster_ds.width,
                "height": rgb_raster_ds.height,
            }
        )

        ghs_img_cropped_filename = "ghs_cropped_" + str(img_number) + ".tif"
        with rasterio.open(
            ghs_img_directory + ghs_img_cropped_filename, "w", **kwargs
        ) as dst:
            reproject(
                source=rasterio.band(ghs_raster_ds, 1),
                destination=rasterio.band(dst, 1),
                src_transform=ghs_raster_ds.transform,
                src_crs=ghs_raster_ds.crs,
                dst_transform=ghs_raster_ds.transform,
                dst_crs=ghs_raster_ds.crs,
                resampling=Resampling.nearest,
            )

        # Assign, to ghs_raster_ds, tif with edited crs
        ghs_raster_ds = rasterio.open(ghs_img_directory + ghs_img_cropped_filename)
        rgb_array_g = rgb_raster_ds.read(2)

        ghs_array = ghs_raster_ds.read(1)

        height, width = rgb_array_g.shape

        mask_dim = 512

        # Individual generators to maintain x-y independence from sampling
        rng_x = np.random.default_rng()
        rng_y = np.random.default_rng()

        masks_processed = 0
        attempts = 0
        max_attempts = 100000
        global aborted_imgs
        while masks_processed < self.masks_num:
            if attempts > max_attempts:
                print("\nReached max attempts for image #", img_number)
                aborted_imgs += 1
                masks_processed += 1
                continue
            try:
                x0 = int(rng_x.random() * (width - mask_dim))
                y0 = int(rng_y.random() * (height - mask_dim))
            except StopIteration:
                print("\nReached end of Iterator.\n")
                break
            ghs_subarray = ghs_array[y0 : y0 + mask_dim, x0 : x0 + mask_dim]

            if self.target_class == 0:
                fill_percentage_of_class = int(
                    (np.count_nonzero(ghs_subarray == 0) / (mask_dim**2) * 100)
                )
            else:
                fill_percentage_of_class = int(
                    (np.count_nonzero(ghs_subarray >= 3) / (mask_dim**2) * 100)
                )

            # Checks whether the target image's representation exceeds the given threshold while also
            # not having a threshold that corresponds to any other of the desired threshold-intervals.
            if (
                fill_percentage_of_class >= self.threshold
                and fill_percentage_of_class < self.threshold + 30
            ):
                # Test if the rgb image contains more than approx. 5% N/A values in the chosen window
                rgb_subarray = rgb_array_g[y0 : y0 + mask_dim, x0 : x0 + mask_dim]
                na_values_threshold = 5
                if (
                    np.count_nonzero(rgb_subarray == 0) / (mask_dim**2) * 100
                    > na_values_threshold
                ):
                    continue

                print("Fill %: {}".format(fill_percentage_of_class))
                masks_processed += 1

                # Extract (save) the 512x512 rgb tiff subarray (with metadata):
                rgb_output_path = (
                    os.getenv("PDG_IMG")
                    + "/training/quota"
                    + planet_quota_num
                    + "/fill_pct_"
                    + str(threshold)
                    + "/"
                    + region_name
                    + "_"
                    + str(img_number)
                    + "_"
                    + str(masks_processed)
                    + "_"
                    + str(threshold)
                    + ".png"
                )

                # The size in pixels of the desired window
                xsize, ysize = mask_dim, mask_dim

                # Create a Window and calculate the transform from the source dataset
                window = Window(x0, y0, xsize, ysize)
                transform = rgb_raster_ds.window_transform(window)

                # Create a new cropped raster to write to and update relevant metadata
                profile = rgb_raster_ds.profile
                profile.update(
                    {
                        "driver": "PNG",
                        "height": xsize,
                        "width": ysize,
                        "count": 3,
                        "transform": transform,
                    }
                )

                with rasterio.open(rgb_output_path, "w", **profile) as dst:
                    # Read the data from the window and write it to the output raster. Omit the fourth band (alpha)
                    raster = rgb_raster_ds.read(window=window)
                    raster = raster[0:3, :]
                    # Write the data to the file
                    dst.write(raster)
                # Remove the aux.xml file that is automatically created with every png
                os.remove(rgb_output_path + ".aux.xml")

                # Extract (save) the sub array that corresponds to the mask:
                mask_output_path = (
                    os.getenv("PDG_IMG")
                    + "/ghs/quota"
                    + planet_quota_num
                    + "/fill_pct_"
                    + str(threshold)
                    + "/"
                    + region_name
                    + "_"
                    + str(img_number)
                    + "_"
                    + str(masks_processed)
                    + "_"
                    + str(threshold)
                    + ".png"
                )

                # Update pixel values that are above 0 to 255 so that the starting greyscale image is transformed to a binary mask that can be used by the model
                ghs_subarray[ghs_subarray > 0] = 255

                transform = ghs_raster_ds.window_transform(window)

                # Create a new cropped raster to write to and update relevant metadata
                profile = ghs_raster_ds.profile
                profile.update(
                    {
                        "height": xsize,
                        "width": ysize,
                        "driver": "PNG",
                        "count": 3,
                        "transform": transform,
                    }
                )

                with rasterio.open(mask_output_path, "w", **profile) as dst:
                    # Read the data from the window and write it to the output raster
                    dst.write(ghs_subarray, indexes=1)
                    dst.write(ghs_subarray, indexes=2)
                    dst.write(ghs_subarray, indexes=3)
                # Remove the aux.xml file that is automatically created with every png
                os.remove(mask_output_path + ".aux.xml")

                print("Saved rgb and mask #{}.".format(masks_processed))
                attempts = 0
            else:
                attempts += 1

        # Clean up the cropped dhs file whose shape matches the original rgb image
        ghs_raster_ds.close()
        os.remove(ghs_img_directory + ghs_img_cropped_filename)


def main():
    print("\n@START ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~\n")

    global rgb_img_directory
    global ghs_img_directory
    global threshold
    global region_name
    global img_number
    global aborted_imgs
    global planet_quota_num

    planet_quota_num = sys.argv[1]
    masks_num = sys.argv[2]
    target_class = sys.argv[3]
    threshold = int(sys.argv[4])

    rgb_img_directory = (
        os.getenv("PDG_IMG_RAW") + "/planet/quota" + planet_quota_num + "/"
    )
    ghs_img_directory = os.getenv("PDG_IMG_RAW") + "/ghs/"

    # Iterates over each image in the directory
    img_aborted_arr = []
    img_number = 0
    aborted_imgs = 0
    region_name = "south"
    for root, dirs, files in os.walk(rgb_img_directory + region_name):
        for tiff_file in files:
            rgb_img_path = os.path.join(root, tiff_file)
            img_path_ghs_raw = (
                ghs_img_directory
                + region_name
                + "/GHS_BUILT_S_E2018_GLOBE_R2022A_54009_10_V1_0_R9_C11.tif"
            )
            ghs_to_binary = CropRawImg(
                rgb_img_path, img_path_ghs_raw, masks_num, target_class, threshold
            )
            ghs_to_binary.gen_masks()
            img_number += 1
    img_aborted_arr.append(aborted_imgs)

    img_number = 0
    aborted_imgs = 0
    region_name = "north"
    for root, dirs, files in os.walk(ghs_img_directory + region_name):
        for tiff_file in files:
            rgb_img_path = os.path.join(root, tiff_file)
            img_path_ghs_raw = (
                ghs_img_directory
                + region_name
                + "/GHS_BUILT_S_E2018_GLOBE_R2022A_54009_10_V1_0_R8_C11.tif"
            )
            ghs_to_binary = CropRawImg(
                rgb_img_path, img_path_ghs_raw, masks_num, target_class, threshold
            )
            ghs_to_binary.gen_masks()
            img_number += 1
    img_aborted_arr.append(aborted_imgs)

    print("\nAborted images per region:\n", img_aborted_arr)
    print("\n@END ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~\n")


if __name__ == "__main__":
    main()

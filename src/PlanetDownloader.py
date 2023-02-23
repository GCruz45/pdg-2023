# Adapted from: https://github.com/planetlabs/notebooks/blob/master/jupyter-notebooks/data-api-tutorials/search_and_download_quickstart.ipynb

import sys
import os
import json
import requests
from requests.auth import HTTPBasicAuth
import webbrowser
from datetime import date


class PlanetDownloader:
    def main(self):

        city_name = ""
        parameters_not_chosen = True
        while parameters_not_chosen:

            def return_bogota_coords():
                # Bogotá, COL bounding box (created via geojson.io)
                geojson_geometry = {
                    "type": "Polygon",
                    "coordinates": [
                        [
                            [-72.51896919172005, 7.909099669847251],
                            [-72.51683996125128, 7.89192592817011],
                            [-72.49119954425231, 7.894037928412686],
                            [-72.50310472142075, 7.908007428804083],
                            [-72.51896919172005, 7.909099669847251],
                        ]
                    ],
                }
                return geojson_geometry

            # List of functions to be used as a switch case to pick target city
            def return_cali_coords():
                # Cali, COL bounding box high-precision (created via geojson.io)
                geojson_geometry = {
                    "type": "Polygon",
                    "coordinates": [
                        [
                            [-76.52667206322685, 3.441571826908344],
                            [-76.54243341850555, 3.392430042567767],
                            [-76.534941909865, 3.352094764224148],
                            [-76.52246706736699, 3.40400952385977],
                            [-76.49057843032784, 3.4326146720879223],
                            [-76.50346250201467, 3.477845356048064],
                            [-76.52667206322685, 3.441571826908344],
                        ]
                    ],
                }
                return geojson_geometry

            def return_medellin_coords():
                # Medellin, COL bounding box (created via geojson.io)
                geojson_geometry = {
                    "type": "Polygon",
                    "coordinates": [
                        [
                            [-75.592142680572, 6.254186517705307],
                            [-75.5840471203619, 6.211518974225484],
                            [-75.59454784710998, 6.176425540662734],
                            [-75.556554151449, 6.236581908506906],
                            [-75.56226215552952, 6.300817930135523],
                            [-75.592142680572, 6.254186517705307],
                        ]
                    ],
                }
                return geojson_geometry

            def return_cartagena_coords():
                # Cartagena, COL bounding box (created via geojson.io)
                geojson_geometry = {
                    "type": "Polygon",
                    "coordinates": [
                        [
                            [-75.49387917989316, 10.323628138494797],
                            [-75.49267955295625, 10.361032655554908],
                            [-75.46615620118715, 10.398780656576221],
                            [-75.51070470430727, 10.40278718307448],
                            [-75.52793638681771, 10.422241894609058],
                            [-75.51296555623114, 10.398335878476033],
                            [-75.49581375052576, 10.358185959836447],
                            [-75.49387917989316, 10.323628138494797],
                        ]
                    ],
                }
                return geojson_geometry

            def return_barranquilla_coords():
                # Barranquilla, COL bounding box (created via geojson.io)
                geojson_geometry = {
                    "type": "Polygon",
                    "coordinates": [
                        [
                            [-74.83723086956395, 11.013655676076013],
                            [-74.8311687855, 10.975016193857329],
                            [-74.81736294281309, 10.93367704846456],
                            [-74.78821350045256, 10.892630183619843],
                            [-74.77720839103141, 10.93129382543178],
                            [-74.80364286968566, 11.009036688237671],
                            [-74.83723086956395, 11.013655676076013],
                        ]
                    ],
                }
                return geojson_geometry

            def return_cucuta_coords():
                # Cúcuta, COL bounding box (created via geojson.io)
                geojson_geometry = {
                    "type": "Polygon",
                    "coordinates": [
                        [
                            [-72.52904139819171, 7.902768323349008],
                            [-72.52685498084625, 7.883637949548714],
                            [-72.50827043341138, 7.882374591820749],
                            [-72.48822827441273, 7.84952593892821],
                            [-72.4528811939974, 7.838876641986488],
                            [-72.45707182724227, 7.9016854956546325],
                            [-72.50735942618418, 7.922078273182308],
                            [-72.52904139819171, 7.902768323349008],
                        ]
                    ],
                }
                return geojson_geometry

            def get_city_coords(city_name):
                switcher = {
                    # 51% pop. 143
                    "bogota": return_bogota_coords,
                    # 16% pop. 45
                    "medellin": return_medellin_coords,
                    # 15% pop. 42
                    "cali": return_cali_coords,
                    # 7.5% pop. 21
                    "cartagena": return_cartagena_coords,
                    # 6.25% pop. 22
                    "barranquilla": return_barranquilla_coords,
                    # 4.19% pop. 12
                    "cucuta": return_cucuta_coords,
                }
                func = switcher.get(city_name, lambda: "Invalid city name.")
                return func()

            city_name = input(
                "Enter desired city name (lowercase). \nAvailable cities: cali, bogota, medellin, cartagena, barranquilla, cucuta.\n"
            )
            geojson_geometry = get_city_coords(city_name)

            # get images that overlap with our AOI
            geometry_filter = {
                "type": "GeometryFilter",
                "field_name": "geometry",
                "config": geojson_geometry,
            }

            # get images acquired within a date range
            date_range_start = input(
                "Enter start range of images (format: YYYY-MM-DD):\n"
            )
            date_range_end = input("Enter end range of images (format: YYYY-MM-DD):\n")
            date_range_filter = {
                "type": "DateRangeFilter",
                "field_name": "acquired",
                "config": {
                    "gte": date_range_start + "T00:00:00.000Z",
                    "lte": date_range_end + "T00:00:00.000Z",
                },
            }

            quality_category_filter = {
                "type": "StringInFilter",
                "field_name": "quality_category",
                "config": ["standard", "beta"],
            }

            # only get images which have under given cloud coverage
            cloud_cover_pct = float(
                input(
                    "Enter desired maximum cloud coverage. Value must fall between [0, 1].\n"
                )
            )
            cloud_cover_filter = {
                "type": "RangeFilter",
                "field_name": "cloud_cover",
                "config": {"lte": cloud_cover_pct},
            }

            # combine our geo, date, cloud filters
            combined_filter = {
                "type": "AndFilter",
                "config": [
                    geometry_filter,
                    date_range_filter,
                    quality_category_filter,
                    cloud_cover_filter,
                ],
            }

            # API Key stored as an env variable
            PLANET_API_KEY = os.getenv("PLANET_API_KEY")

            ## Select aircraft/item_type
            # For PlanetScope2:
            item_type = "PSScene3Band"
            # For SkySat (very high res):
            # item_type = "SkySatCollect"
            # For Landsat8:
            # item_type = "Landsat8L1G"

            asset_type = "visual"  # Works with both PS and Landsat8
            # asset_type = 'ortho_visual' # Works with SkySat

            # API request object
            search_request = {"item_types": [item_type], "filter": combined_filter}

            # fire off the POST request
            print("\nStarting Search...\n")
            search_result = requests.post(
                "https://api.planet.com/data/v1/quick-search",
                auth=HTTPBasicAuth(PLANET_API_KEY, ""),
                json=search_request,
            )

            geojson = search_result.json()

            # extract image IDs only
            image_ids = [feature["id"] for feature in geojson["features"]]
            continue_flag = input(
                "Images found for city {}: {}.\nPress 'y' to continue, or enter to return.\n".format(
                    city_name, len(image_ids)
                )
            )
            if continue_flag == "y":
                parameters_not_chosen = False

        # Determine the range of IDs of the images to be obtained
        img_id_range = input("Enter desired image id range (e.g: 10-12):\n")
        print("Ids: {}\n".format(img_id_range))
        start_id = int(img_id_range.split("-")[0])
        end_id = int(img_id_range.split("-")[1]) + 1

        status_array = []
        for img_id in range(start_id, end_id):
            print("Processing Id {}".format(img_id))
            img_id = int(img_id)
            id0 = image_ids[img_id]
            id0_url = (
                "https://api.planet.com/data/v1/item-types/{}/items/{}/assets".format(
                    item_type, id0
                )
            )

            # Returns JSON metadata for assets in this ID. Learn more: planet.com/docs/reference/data-api/items-assets/#asset
            result = requests.get(id0_url, auth=HTTPBasicAuth(PLANET_API_KEY, ""))

            # List of asset types available for this particular satellite image
            print("Assets available for image of id = {}:".format(img_id))
            print(result.json().keys())

            # This is "inactive" if the "visual" asset has not yet been activated; otherwise 'active'
            print(result.json()[asset_type]["status"] + "\n")

            # Parse out useful links
            links = result.json()[asset_type]["_links"]
            self_link = links["_self"]
            activation_link = links["activate"]

            # Request activation of the 'visual' asset:
            activate_result = requests.get(
                activation_link, auth=HTTPBasicAuth(PLANET_API_KEY, "")
            )

            status_array.append(self_link)

        flag = False
        download_links_array = []
        active_assets = 0
        total_imgs = len(status_array)
        # while activation_status_result.json()["status"] != "active":
        while flag != True:
            for self_link in status_array:
                activation_status_result = requests.get(
                    self_link, auth=HTTPBasicAuth(PLANET_API_KEY, "")
                )
                if activation_status_result.json()["status"] == "active":
                    active_assets += 1
                    download_links_array.append(
                        activation_status_result.json()["location"]
                    )
                    status_array.remove(self_link)

            prompt_to_proceed = input(
                "{}/{} assets ready to download.\nPress 'enter' to retry, or 'y' to continue: ".format(
                    str(active_assets), total_imgs
                )
            )
            if prompt_to_proceed == "y":
                flag = True

        print("\nOpening browser to begin download...\n")
        for download_link in download_links_array:
            webbrowser.open(download_link)

        # Append downloaded Id range to text file for future reference.
        download_date_log_file_name = (
            "ids_of_downloaded_imgs_"
            + city_name
            + "_"
            + date.today().strftime("%B-%d-%Y")
            + ".txt"
        )
        with open(download_date_log_file_name, "a+") as file_object:
            total_downloaded = (
                str(active_assets) + "/" + str(int(end_id) - int(start_id))
            )
            current_date = date.today().strftime("%B %d, %Y")
            print("Writing log to {}...\n".format(download_date_log_file_name))
            file_object.write(
                "IDs Range: {}. Total Downloaded: {}. Date of download: {}\n\n".format(
                    img_id_range, total_downloaded, current_date
                )
            )


if __name__ == "__main__":
    PlanetDownloader().main()

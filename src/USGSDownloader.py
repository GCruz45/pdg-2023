# =============================================================================
#  USGS/EROS Inventory Service Example
#  Description: Download Landsat Collection 2 files
#  Usage: python download_sample.py -u username -p password -f filetype
#         optional argument f refers to filetype including 'bundle' or 'band'
# =============================================================================

import json
import requests
import sys
import time
import argparse
import re
import threading
import datetime
import os


class USGSDownloader:

    def __init__(self, scene_source="request"):
        self.scene_source = scene_source
        self.idField = "displayId"
        self.datasetName = "gls_all"
        self.maxResults = 10
        self.path = ""  # Fill a valid download path
        self.maxthreads = 5  # Threads count for downloads
        self.sema = threading.Semaphore(value=self.maxthreads)
        self.label = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")  # Customized label using date time
        self.threads = []
        # The entityIds/displayIds need to save to a text file such as scenes.txt.
        # The header of text file should follow the format: datasetName|displayId or datasetName|entityId.
        # sample file - scenes.txt
        # landsat_ot_c2_l2|displayId
        # LC08_L2SP_012025_20201215_20201219_02_T1
        # LC08_L2SP_012027_20201215_20201219_02_T1
        self.scenesFile = 'scenes.txt'

    # Send http request
    def sendRequest(self, url, data, apiKey=None, exitIfNoResponse=True):
        json_data = json.dumps(data)

        if apiKey == None:
            response = requests.post(url, json_data)
        else:
            headers = {'X-Auth-Token': apiKey}
            response = requests.post(url, json_data, headers=headers)

        try:
            httpStatusCode = response.status_code
            if response == None:
                print("No output from service")
                if exitIfNoResponse:
                    sys.exit()
                else:
                    return False
            output = json.loads(response.text)
            if output['errorCode'] != None:
                print(output['errorCode'], "- ", output['errorMessage'])
                if exitIfNoResponse:
                    sys.exit()
                else:
                    return False
            if httpStatusCode == 404:
                print("404 Not Found")
                if exitIfNoResponse:
                    sys.exit()
                else:
                    return False
            elif httpStatusCode == 401:
                print("401 Unauthorized")
                if exitIfNoResponse:
                    sys.exit()
                else:
                    return False
            elif httpStatusCode == 400:
                print("Error Code", httpStatusCode)
                if exitIfNoResponse:
                    sys.exit()
                else:
                    return False
        except Exception as e:
            response.close()
            print(e)
            if exitIfNoResponse:
                sys.exit()
            else:
                return False
        response.close()

        return output['data']

    def downloadFile(self, url):
        self.sema.acquire()
        try:
            response = requests.get(url, stream=True)
            disposition = response.headers['content-disposition']
            filename = re.findall("filename=(.+)", disposition)[0].strip("\"")
            print(f"Downloading {filename} ...\n")
            if self.path != "" and self.path[-1] != "/":
                filename = "/" + filename
            filename = "../../img/usgs_imgs/" + filename
            open(self.path + filename, 'wb').write(response.content)
            print(f"Downloaded {filename}\n")
            self.sema.release()
        except Exception as e:
            print(f"Failed to download from {url}. Will try to re-download.")
            self.sema.release()
            self.runDownload(self.threads, url)

    def runDownload(self, threads, url):
        thread = threading.Thread(target=self.downloadFile, args=(url,))
        threads.append(thread)
        thread.start()

    def get_scenes_from_file(self):
        # Read scenes
        f = open(self.scenesFile, "r")
        lines = f.readlines()
        f.close()
        header = lines[0].strip()
        self.datasetName = header[:header.find("|")]
        self.idField = header[header.find("|") + 1:]

        print("Scenes details:")
        print(f"Dataset name: {self.datasetName}")
        print(f"Id field: {self.idField}\n")

        lines.pop(0)
        return lines

    def get_payload_of_scenes_from_request(self,
                                           dataset_name="gls_all",
                                           max_results=3,
                                           starting_number=1,
                                           metadata_type="summary",
                                           ll_corner=[40, -120],
                                           ur_corner=[50, -100],
                                           cloud_filter_max=50,
                                           cloud_filter_min=0):
        # Search scenes
        # https://m2m.cr.usgs.gov/api/docs/reference/#scene-search

        # Coordenadas Cali
        #lower_left_corner = {
        #     "latitude": 3.4569,
        #     "longitude": -76.5542
        #}
        #upper_right_corner = {
        #    "latitude": 3.4484,
        #     "longitude": -76.5444
        #}

        # Coordenadas Bogotá
        lower_left_corner = {
             "latitude": 4.473854,
             "longitude": -74.299741
        }
        upper_right_corner = {
             "latitude": 4.784290,
             "longitude":  -73.953730
        }
        # lower_left_corner = {
        #     "latitude": ll_corner[0],
        #    "longitude": ll_corner[1]
        #}
        #upper_right_corner = {
        #    "latitude": ur_corner[0],
        #    "longitude": ur_corner[1]
        #}
        spatial_filter = {
            "filterType": "mbr",
            "lowerLeft": lower_left_corner,
            "upperRight": upper_right_corner
        }
        cloud_cover_filter = {
            "max": cloud_filter_max,
            "min": cloud_filter_min,
            "includeUnknown": False
        }
        # Pre-SLC sensor failure of Landsat7:
        #acquisition_filter = {
        #    "start": "1999-04-20",
        #    "end": "2003-04-30"
        #}
        
        # Gap masks are included on all Landsat 7 ETM+ SLC-off imagery processed on or after December 11, 2008
        acquisition_filter = {
            "start": "2008-12-12",
            "end": "2022-04-30"
        }
        payload = {
            "datasetName": dataset_name,  # Used to identify the dataset to search
            "maxResults": max_results,  # How many results should be returned ? (default = 100)
            "startingNumber": starting_number,  # Used to identify the start number to search from
            "metadataType": metadata_type,  # If populated, identifies which metadata to return (summary or full)
            "sceneFilter": {
                #"acquisitionFilter": acquisition_filter,
                "acquisitionFilter": None,
                "cloudCoverFilter": cloud_cover_filter,
                "ingestFilter": None,
                "metadataFilter": None,
                "spatialFilter": spatial_filter,
            },
            "compareListName": None,  # If provided, defined a scene-list listId to use to track
            # scenes selected for comparison
            "bulkListName": None,  # If provided, defined a scene-list listId to use to track
            # scenes selected for bulk ordering
            "orderListName": None,  # If provided, defined a scene-list listId to use to track
            # scenes selected for on-demand ordering
            "excludeListName": None  # If provided, defined a scene-list listId to use to exclude
            # scenes from the results
        }
        return payload

    # # corners[0] is the lower left corner and corners[1] is the upper right corner.
    # def create_spatial_filter(self, corners): # TODO
    #     return

    def main(self):
        #  Usage: python USGSDownloader.py -u username -p password -f filetype
        #         optional argument f refers to filetype including 'bundle' or 'band'
        # User input
        parser = argparse.ArgumentParser()
        parser.add_argument('-u', '--username', required=False, help='Username', default=os.getenv('USGS_USER'))
        parser.add_argument('-p', '--password', required=False, help='Password', default=os.getenv('USGS_PASSWD'))
        parser.add_argument('-f', '--filetype', required=False, choices=['bundle', 'band'],
                            help='File types to download, "bundle" for bundle files and "band" for band files')

        args = parser.parse_args()

        username = args.username
        password = args.password
        filetype = args.filetype

        print("\nRunning Scripts...\n")
        startTime = time.time()

        serviceUrl = "https://m2m.cr.usgs.gov/api/api/json/stable/"

        # Login
        payload = {'username': username, 'password': password}
        apiKey = self.sendRequest(serviceUrl + "login", payload)
        print("API Key: " + apiKey + "\n")

        entityIds = []

        if self.scene_source == "file":
            lines = self.get_scenes_from_file()
            for line in lines:
                entityIds.append(line.strip())
        elif self.scene_source == "request":
            payload = self.get_payload_of_scenes_from_request()
            results = self.sendRequest(serviceUrl + "scene-search", payload, apiKey)
            print(results['results'])
            results = results['results']
            for result in results:
                # print(result)
                entityIds.append(result['entityId'])

        # Add scenes to a list
        listId = f"temp_{self.datasetName}_list"  # customized list id
        print("listId: " + listId)
        payload = {
            "listId": listId,
            'idField': self.idField,
            "entityIds": entityIds,
            "datasetName": self.datasetName
        }

        print("Adding scenes to list...\n")
        count = self.sendRequest(serviceUrl + "scene-list-add", payload, apiKey)
        print("Added", count, "scenes\n")

        # Get download options
        payload = {
            "listId": listId,
            "datasetName": self.datasetName
        }

        print("Getting product download options...\n")
        products = self.sendRequest(serviceUrl + "download-options", payload, apiKey)
        print("Got product download options\n")

        # Select products
        downloads = []
        if filetype == 'bundle':
            # select bundle files
            for product in products:
                if product["bulkAvailable"]:
                    downloads.append({"entityId": product["entityId"], "productId": product["id"]})
        elif filetype == 'band':
            # select band files
            for product in products:
                if product["secondaryDownloads"] is not None and len(product["secondaryDownloads"]) > 0:
                    for secondaryDownload in product["secondaryDownloads"]:
                        if secondaryDownload["bulkAvailable"]:
                            downloads.append(
                                {"entityId": secondaryDownload["entityId"], "productId": secondaryDownload["id"]})
        else:
            # select all available files
            for product in products:
                if product["bulkAvailable"]:
                    downloads.append({"entityId": product["entityId"], "productId": product["id"]})
                    if product["secondaryDownloads"] is not None and len(product["secondaryDownloads"]) > 0:
                        for secondaryDownload in product["secondaryDownloads"]:
                            if secondaryDownload["bulkAvailable"]:
                                downloads.append(
                                    {"entityId": secondaryDownload["entityId"], "productId": secondaryDownload["id"]})

        # Remove the list
        payload = {
            "listId": listId
        }
        self.sendRequest(serviceUrl + "scene-list-remove", payload, apiKey)

        # Send download-request
        payLoad = {
            "downloads": downloads,
            "label": self.label,
            'returnAvailable': True
        }

        print(f"Sending download request ...\n")
        results = self.sendRequest(serviceUrl + "download-request", payLoad, apiKey)
        print(f"Done sending download request\n")

        for result in results['availableDownloads']:
            print(f"Get download url: {result['url']}\n")
            self.runDownload(self.threads, result['url'])

        preparingDownloadCount = len(results['preparingDownloads'])
        preparingDownloadIds = []
        if preparingDownloadCount > 0:
            for result in results['preparingDownloads']:
                preparingDownloadIds.append(result['downloadId'])

            payload = {"label": self.label}
            # Retrieve download urls
            print("Retrieving download urls...\n")
            results = self.sendRequest(serviceUrl + "download-retrieve", payload, apiKey, False)
            if results != False:
                for result in results['available']:
                    if result['downloadId'] in preparingDownloadIds:
                        preparingDownloadIds.remove(result['downloadId'])
                        print(f"Get download url: {result['url']}\n")
                        self.runDownload(self.threads, result['url'])

                for result in results['requested']:
                    if result['downloadId'] in preparingDownloadIds:
                        preparingDownloadIds.remove(result['downloadId'])
                        print(f"Get download url: {result['url']}\n")
                        self.runDownload(self.threads, result['url'])

            # Don't get all download urls, retrieve again after 30 seconds
            while len(preparingDownloadIds) > 0:
                print(
                    f"{len(preparingDownloadIds)} downloads are not available yet. Waiting for 30s to retrieve again\n")
                time.sleep(30)
                results = self.sendRequest(serviceUrl + "download-retrieve", payload, apiKey, False)
                if results != False:
                    for result in results['available']:
                        if result['downloadId'] in preparingDownloadIds:
                            preparingDownloadIds.remove(result['downloadId'])
                            print(f"Get download url: {result['url']}\n")
                            self.runDownload(self.threads, result['url'])

        print("\nGot download urls for all downloads\n")
        # Logout
        endpoint = "logout"
        if self.sendRequest(serviceUrl + endpoint, None, apiKey) == None:
            print("Logged Out\n")
        else:
            print("Logout Failed\n")

        print("Downloading files... Please do not close the program\n")
        for thread in self.threads:
            thread.join()

        print("Complete Downloading")

        executionTime = round((time.time() - startTime), 2)
        print(f'Total time: {executionTime} seconds')


if __name__ == '__main__':
    USGSDownloader().main()

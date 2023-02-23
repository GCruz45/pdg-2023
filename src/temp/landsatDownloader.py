import os
from landsatxplore.api import API
from landsatxplore.earthexplorer import EarthExplorer

class landsatDownloader:
     
	str LANDSATXPLORE_USERNAME="GCruz45"
	str LANDSATXPLORE_PASSWORD="GCL268425piscis"

	def __init__(self, imgSource):
		# Initialize a new API instance and get an access key
		api = API(LANDSATXPLORE_USERNAME, LANDSATXPLORE_PASSWORD)

	# Perform a request. Results are returned in a dictionnary
	response = api.request(
	    '<request_endpoint>',
	    params={
		"param_1": value_1,
		"param_2": value_2
	    }
	)


	# Search for Landsat TM scenes
	def getScenes():
		scenes = api.search(
		    dataset='landsat_tm_c1',
		    latitude=50.85,
		    longitude=-4.35,
		    start_date='1995-01-01',
		    end_date='1995-10-01',
		    max_cloud_cover=10
		)

		print(f"{len(scenes)} scenes found.")

		# Process the result
		for scene in scenes:
		    print(scene['acquisition_date'])
		    # Write scene footprints to disk
		    fname = f"{scene['landsat_product_id']}.geojson"
		    with open(fname, "w") as f:
			json.dump(scene['spatialCoverage'], f)

	def downloadScene(scene, target_dir):
		ee = EarthExplorer(username, password)

		ee.download(scene_id='LT51960471995178MPS00', output_dir='./data')

		ee.logout()

	# Log out
	api.logout()

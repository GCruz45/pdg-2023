import os
import json
import requests
from requests.auth import HTTPBasicAuth

class PlanetDownloader:
     
#	def __init__(self, imgSource):
#		return None

       # Create a geoJsonObject from two opposing corners in lat-long format.
	def create_geo_object(self, corner1, corner3):
	    corner2 = [corner1[1], corner3[0]]
	    corner4 = [corner1[0], corner3[1]]

	    geojson_obj = {
	  "type": "Polygon",
	  "coordinates": [[
			  corner1,
			  corner2, 
			  corner3, 
			  corner4, 
			  corner1
			  ]]
	    }
	    return geojson_obj

	# Get images that overlap with our AOI 
	def get_geo_filter(self, geojson_geometry):

	  geometry_filter = {
	    "type": "GeometryFilter",
	    "field_name": "geometry",
	    "config": geojson_geometry
	  }
	  return geometry_filter

	# Gets the date range filter from a given starting and ending date. 
	# Uses YYYY-MM-DD format.
	def get_sat_images_date_range_filter(self, start_date, end_date):
	  gte = start_date + "T00:00:00.000Z"
	  lte = end_date + "T00:00:00.000Z"

	  date_range_filter = {
	  "type": "DateRangeFilter",
	  "field_name": "acquired",
	  "config": {
	    "gte": gte,
	    "lte": lte
	    }
	  }

	  return date_range_filter

	# Gets the cloud coverage filter. Param: Cloud coverage % (in decimal). 
	# Uses YYYY-MM-DD format.
	def get_sat_images_cloud_cover_filter(self, cloudCoverPercentage):
	  cloud_cover_filter = {
	    "type": "RangeFilter",
	    "field_name": "cloud_cover",
	    "config": {
	      "lte": cloudCoverPercentage
	    }
	  }

	  return cloud_cover_filter

	# combine our geo, date, cloud filters
	def get_combined_filter(self, geo_filter, date_filter, cloud_filter):

	  combined_filter = {
	    "type": "AndFilter",
	    "config": [geo_filter, date_filter, cloud_filter]
	  }
	  return combined_filter

	def post_request(self, combined_filter):
		# API request object
		search_request = {
		  # "interval": "day",
		  "item_types": [item_type], 
		  "filter": combined_filter
		}

		# fire off the POST request
		search_result = \
		  requests.post(
		    'https://api.planet.com/data/v1/quick-search',
		    auth=HTTPBasicAuth(PLANET_API_KEY, ''),
		    json=search_request)

		#print(json.dumps(search_result.json(), indent=1))
		
		return search_result

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ #

# API Key stored as an env variable
#PLANET_API_KEY = 'PLAK67d404bdfc3b4ded8cb39e130cba3f2d'
PLANET_API_KEY = os.getenv('PL_API_KEY')
item_type = "PSScene3Band"


caliCoords =             [
              -81.44439697265624,
              25.735580912151537
            ],            [
              -80.1507568359375,
              26.613085653537333
            ]

corner1 = [
              -81.44439697265624,
              25.735580912151537
            ]
            
corner3 = [
              -80.1507568359375,
              26.613085653537333
            ]

planet_download = PlanetDownloader()

geojson_geometry = planet_download.create_geo_object(corner1, corner3)

start_date = "2018-05-20"
end_date = "2018-07-20"
cloud_coverage = 0.5

geo_filter = planet_download.get_geo_filter(geojson_geometry)
date_filter = planet_download.get_sat_images_date_range_filter(start_date, end_date)
cloud_filter = planet_download.get_sat_images_cloud_cover_filter(cloud_coverage)

combined_filter = planet_download.get_combined_filter(geo_filter, date_filter, cloud_filter) 
search_result = planet_download.post_request(combined_filter)

# extract image IDs only from the previous search results.
image_ids = [feature['id'] for feature in search_result.json()['features']]
print(image_ids)

# For demo purposes, just grab the first image ID
id0 = image_ids[1]
id0_url = 'https://api.planet.com/data/v1/item-types/{}/items/{}/assets'.format(item_type, id0)

# Returns JSON metadata for assets in this ID. Learn more: planet.com/docs/reference/data-api/items-assets/#asset
result = \
  requests.get(
    id0_url,
    auth=HTTPBasicAuth(PLANET_API_KEY, '')
  )

# List of asset types available for this particular satellite image
print(result.json().keys())

# This is "inactive" if the "visual" asset has not yet been activated; otherwise 'active'
print(result.json()['visual']['status'])



# Parse out useful links
links = result.json()[u"visual"]["_links"]
self_link = links["_self"]
activation_link = links["activate"]

# Request activation of the 'visual' asset:
activate_result = \
  requests.get(
    activation_link,
    auth=HTTPBasicAuth(PLANET_API_KEY, '')
  )



activation_status_result = \
  requests.get(
    self_link,
    auth=HTTPBasicAuth(PLANET_API_KEY, '')
  )
    
print(activation_status_result.json()["status"])

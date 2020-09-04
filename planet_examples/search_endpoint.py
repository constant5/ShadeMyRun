import os
import requests
from requests.auth import HTTPBasicAuth
import pprint
import json

# our demo filter that filters by geometry, date and cloud cover
from demo_filters import redding_reservoir

# Search API request object
search_endpoint_request = {
  "item_types": ["REOrthoTile"],
  "filter": redding_reservoir
}

result = \
  requests.post(
    'https://api.planet.com/data/v1/quick-search',
    auth=HTTPBasicAuth(os.environ['PL_API_KEY'], ''),
    json=search_endpoint_request)


info = json.loads(result.text)
# pprint.pprint(info)
# print(result.text)

pprint.pprint(info['features'][3]['properties'])
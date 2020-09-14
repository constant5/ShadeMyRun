import requests
import re

# Initial info
API_key = "key"

# API URLs
path_url = "https://roads.googleapis.com/v1/snapToRoads?"

map_url  = "https://maps.googleapis.com/maps/api/staticmap?"

# Directions API
origin = input('where are you? ').replace(' ' ,'+')
destination = input('Where do you want to go? ').replace(' ','+')
coordinates = 'origin={}&destination={}&mode=walking&key={}'.format(origin, destination, API_key)

directions_api = "https://maps.googleapis.com/maps/api/directions/json?"

request_1 = directions_api + coordinates
response_1 = requests.get(request_1)

directions = response_1.json()

# Get coordinates list
gps_coord = []
for i in directions['routes'][0]['legs'][0]['steps']:
    gps_coord.append(i['start_location'])
    
center = str([gps_coord[0]['lat'], gps_coord[0]['lng']]
             ).strip('[]').replace(' ','')

# Obtain GPS Path
gps_string = str(gps_coord)
gps_clean = gps_string.replace('},', '|')
coordinates_path_list = re.sub(r'[{}\'latng: \[\]]', '', gps_clean)



path_parameters = 'path={}&key={}'.format(coordinates_path_list, API_key)
request_2 = path_url  + path_parameters

response_2 = requests.get(request_2)

path = response_2.json()

print(path)



# Default Static Map Parameters 
size = '500x500'
scale = '2'
image_format = 'jpg'
maptype = 'satellite'

# marker_style gets formatted like marker coordinate
parameters = 'size={}&scale={}&format={}&maptype={}&path=color:0xff0000ff|weight:2|{}&key={}'.format(size, scale, image_format, maptype, coordinates_path_list, API_key)

request_3 = map_url + parameters
response_3 = requests.get(request_3)

# Open Image
print(request_3)

import webbrowser  
webbrowser.open(request_3, new=0, autoraise=True)
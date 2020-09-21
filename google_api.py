import requests
import re
import webbrowser

class Coordinates:
    def __init__(self, origin, destination):
        # Initial info
        self.origin = origin.replace(' ' ,'+')
        self.destination = destination.replace(' ','+')
        self.key = "API key"
        self.directions_url = "https://maps.googleapis.com/maps/api/directions/json?"
        self.map_url  = "https://maps.googleapis.com/maps/api/staticmap?"
        self.gps_coord_pairs = []
    
        # Directions API
        coordinates = 'origin={}&destination={}&mode=walking&key={}'.format(self.origin, self.destination, self.key)
        request_1 = self.directions_url + coordinates
        response_1 = requests.get(request_1)
        directions = response_1.json()
        
        self.gps_coord = []
        
        # Get coordinates list
        for i in directions['routes'][0]['legs'][0]['steps']:
            self.gps_coord.append(i['start_location'])
            
        self.gps_coord_pairs = []
        
        for dictionary in self.gps_coord:
            pair = list(dictionary.values())
            self.gps_coord_pairs.append(pair)
                    
    def split_coord(self):
        lat_list = [i[0] for i in self.gps_coord_pairs]  
        lng_list = [i[1] for i in self.gps_coord_pairs] 
           
        print("final lists", str(lat_list), "\n", str(lng_list))  
    
    
                
    
    def return_image(self):
        gps_string = str(self.gps_coord)
        gps_clean = gps_string.replace('},', '|')
        coordinates_path_list = re.sub(r'[{}\'latng: \[\]]', '', gps_clean)

        # Default Static Map Parameters 
        size = '500x500'
        scale = '2'
        image_format = 'jpg'
        maptype = 'satellite'
        
        # marker_style gets formatted like marker coordinate
        parameters = 'size={}&scale={}&format={}&maptype={}&path=color:0xffffff50|weight:5|{}&key={}'.format(size, scale, image_format, maptype, coordinates_path_list, self.key)
        
        request_2 = self.map_url + parameters
        
        # Open Image
        # print(request_2)
        
        webbrowser.open(request_2, new=0, autoraise=True)
        
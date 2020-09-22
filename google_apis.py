import requests
import re
import webbrowser

# Directions API / Static Maps API Documentation
# https://developers.google.com/maps/documentation/directions/overview
# https://developers.google.com/maps/documentation/maps-static/overview

class Coordinates:
    def __init__(self, origin, destination):
        '''Setup attributes, including API urls'''
        
        self.origin = origin.replace(' ' ,'+')
        self.destination = destination.replace(' ','+')
        self.key = "API Key"
        self.directions = "https://maps.googleapis.com/maps/api/directions/json?"
        self.maps_static  = "https://maps.googleapis.com/maps/api/staticmap?"
        self.gps_coord_pairs = []
    

    def return_coordinates(self):
        '''Returns coordinates for a given route based on 'steps' on google maps
        Ex: 'Turn left at this intersection' = gps coordinate'''
        
        # Combine parameters with Directions API URL
        coordinates = ('origin={}&destination={}&mode=walking&key={}'.
                       format(self.origin, self.destination, self.key)
                       )
        
        request_1 = self.directions + coordinates
        response_1 = requests.get(request_1)
        directions = response_1.json()
        
        # Get coordinates list (of dictionaries)
        self.gps_coord = []
        for i in directions['routes'][0]['legs'][0]['steps']:
            self.gps_coord.append(i['start_location'])
         
        # Turn into list of lists (Lat/Lng pairs)
        self.gps_coord_pairs = []
        for dictionary in self.gps_coord:
            pair = list(dictionary.values())
            self.gps_coord_pairs.append(pair)
            
        return self.gps_coord_pairs
            
                    
    def split_coord(self):
        '''Separates GPS pairs into two lists for Lat and Lng'''
        
        lat_list = [i[0] for i in self.gps_coord_pairs]  
        lng_list = [i[1] for i in self.gps_coord_pairs] 
           
        print(lat_list, lng_list, sep='\n')    

    '''
        This method is for future purposes.
        The goal here is to create a bounding box for a given route by
        calculating gps location in relation to other pairs in the route (N vs S vs W vs E)
        
    def box_seg_1(self):
        #Determine if x or y axis segment (N/S or E/W running bounding box) 
        lat_dif_1 = [lat_list[0] - lat_list[1]]
        lng_dif_1 = [lng_list[0] - lng_list[1]] 
        OFFSET = 0.00006 # OFFSET allows for 13.4 meter wide box along axis (6.7m both sides of road)
        if lat_dif_1 > lng_dif_1: # greater differnece in latitude indicate x-axis (north-south) 
            bb_pt1 = lat_list[0], lng_list[0] + OFFSET
            bb_pt2 = lat_list[0], lng_list[0] - OFFSET
            bb_pt3 = lat_list[1], lng_list[1] + OFFSET
            bb_pt4 = lat_list[1], lng_list[1] - OFFSET
        else: # greater difference in longitude indicates y-axis (east-west)
            bb_pt1 = lat_list[0] + OFFSET, lng_list[0]
            bb_pt2 = lat_list[0] - OFFSET, lng_list[0]
            bb_pt3 = lat_list[1] + OFFSET, lng_list[1]
            bb_pt4 = lat_list[1] - OFFSET, lng_list[1]
        # Create bb_seg1 to set as static map poly-line parameters 
             bb_seg1 = bb_pt1, bb_pt2, bb_pt3, bb_pt4
            print(bb_seg1)
            #Need to build in loop function to perform on multiple legs of route
    '''
    
    def return_image(self):
        '''Returns an image of the route produced from given origin/destination'''
        # Clean gps_coord to use as parameter
        gps_string = str(self.gps_coord)
        gps_clean = gps_string.replace('},', '|')
        coordinates_path_list = re.sub(r'[{}\'latng: \[\]]', '', gps_clean)

        # Default Maps Static API parameters 
        size = '500x500'
        scale = '2'
        image_format = 'jpg'
        maptype = 'satellite'
        route_style = 'color:0xffffff50|weight:5|'
        
        # Combine parameters with Maps Static API URL
        parameters = ('size={}&scale={}&format={}&maptype={}&path={}{}&key={}'.
                      format(size, scale, image_format, maptype,
                             route_style, coordinates_path_list, self.key)
                      )
        
        # Display Image in URL
        request_2 = self.maps_static + parameters
        webbrowser.open(request_2, new=0, autoraise=True)
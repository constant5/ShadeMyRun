from PIL import Image
import os
import json
import xmltodict
from pascal_voc_writer import Writer


class image_cropper:
    # This class provides the ability to separate the images into tiles of height x width size
    # The leftover edges are dropped and it returns a dictionary of crop_boxes[image_tile_name] = (bounds for section of image)
    # This box is given so that it can be used to separate the bounding boxes of corresponding VOC files (or other labeled training data)
    def __crop(self,infile,height,width):
        '''Internal class that crops a specific image into tiles. 
        Parameters
        ----------
        infile : str
            the file path and name of an image 
        height : int
            the desired tile height
        width : int
            the desired tile width
        Returns
        -------
        The image tiles via generator
        '''
        with Image.open(infile) as im:
            imgwidth, imgheight = im.size
            for i in range(imgheight//height):
                for j in range(imgwidth//width):
                    box = (j*width, i*height, (j+1)*width, (i+1)*height)
                    yield (box, im.crop(box))

    def crop(self,infile,outfolder,height,width,start_num):
        '''Wrapper for the internal crop function that handles the 
             management of file names as well as saving the new images. 
        Parameters
        ----------
        infile : str
            the file path and name of an image 
        outfolder : str
            the folder that the tile png's should be written to 
        height : int
            the desired tile height
        width : int
            the desired tile width
        start_num : int
            the number that will be used to start file numbering
        Returns
        -------
        Dictionary of crop_boxes[image_tile_name] = (bounds for section of image)
        '''
        crop_boxes = dict()
        for k,(box,piece) in enumerate(self.__crop(infile,height,width),start_num):
            img=Image.new('RGB', (height,width), 255)
            img.paste(piece)
            img_name = infile.split("\\")[-1]
            img_name = "%s-%s.png" % (img_name, k)
            path=os.path.join(outfolder,img_name)
            img.save(path)
            crop_boxes[path] = box
        return crop_boxes

class voc_tiler: 
    # This class takes a given VOC/Pascal annotated file and divides itself and associated image up into corresponding tiles
    # e.g. a 1920 x 1080 image broken could be broken into a 3 by 2 grid of 512 x 512 images (The leftover area is discarded) 
    def __init__(self):
        ''' json_body will store the incoming voc file for easy parsing
            image_tile_boxes is a dictionary of image_tile_name => (bounds for section of image)
            image_data_points is a dictionary of image_tile_name and the associated bounding boxes found in
              the original data set
            new_voc_files is a dictionary of voc_file_name -> voc data to be written to file
        '''
        self.json_body = None
        #self.image_tile_boxes[<image>] = <box encompased>
        self.image_tile_boxes = dict()
        self.image_data_points = dict()
        self.new_voc_files = dict()

    def __crop_image(self,infile,outfolder,height,width,start_number):
        '''Wrapper for the image_cropper crop function
            See image_cropper.crop() for parameter details
        '''
        ic = image_cropper()
        box_dict = ic.crop(infile,outfolder,height,width,start_num)
        return box_dict

    def __parse_voc_file(self,infile):
        '''Reads a voc file into the json body for easy parsing
        '''
        with open(infile) as xml_file:
            data_dict = xmltodict.parse(xml_file.read())
            self.json_body = json.dumps(data_dict)

    def split_voc_and_images(self,xmlfile,outfolder,height,width,start_num):
        '''Overall logic funtion
          1. Parses Voc file into json body
          2. crop image to given measurements and retrieve dictionary of image name / bounding boxes
          3. loop through bounding boxes and find associated data points 
            3b. If bounding box overlaps tiles, shorten the box to fit in its corresponding tile
          4. Create the object list that represents each bounding box for a given image
          5. Create object that represents a single one of the VOC tiles and place it in self.new_voc_files

        '''
        self.__parse_voc_file(xmlfile)
        self.image_tile_boxes = self.__crop_image(self.json_body["annotation"]["path"],outfolder,height,width,start_num)
        min_points = 0
        #TODO Doesn't handle incrementing files (just does bounding boxes vs points, not conversion to 
        # new points -> subtract minimum of bounding box)
        for index, image_file in enumerate(self.image_tile_boxes.keys()):
            bounding_box = self.image_tile_boxes[image_file]
            self.image_data_points[image_file]["object"] = []
            for data_point in self.json_body["annotation"]["object"]:
                x_min = data_point["bndbox"]["xmin"]
                x_max = data_point["bndbox"]["xmax"]
                y_min = data_point["bndbox"]["ymin"]
                y_max = data_point["bndbox"]["ymax"]
                
                x_in_bounds = x_min >= bounding_box[0] or x_max >= bounding_box[2]
                y_in_bounds = y_min >= bounding_box[3] or y_max >= bounding_box[1]
                if x_in_bounds and y_in_bounds:
                    if x_min < bounding_box[0]:
                        x_min = bounding_box[0]
                    x_min = x_min - bounding_box[0]
                    if x_max > bounding_box[2]:
                        x_max = bounding_box[2]
                    x_max = x_max - bounding_box[2]
                    if y_min < bounding_box[3]:
                        y_min = bounding_box[3]
                    y_min = y_min - bounding_box[3]
                    if y_max > bounding_box[1]:
                        y_max = bounding_box[1]
                    y_max = y_max - bounding_box[1]

                    data_object = {"name":data_point["name"], "pose":data_point["pose"], 
                        "truncated":data_point["truncated"], "difficult":data_point["difficult"], 
                        "bndbox":{"xmin":x_min, "ymin":y_min, "xmax":x_max, "ymax":y_max}}
                    self.image_data_points[image_file]["object"].append(data_object)
                    min_points += 1

            #Check if there's at least 1 bounding box in the tile before creating a new file
            if min_points:
                folder = outfolder
                filename = image_file.split("\\")[-1]
                path = image_file
                source = self.json_body["annotation"]["source"]
                size = {"size":{"width":width,"height":height,"depth":3}}
                segmented = self.json_body["annotation"]["segmented"]
                #data_object
                xml_filename = xmlfile.split("\\")[-1].split(".")[-1] + str(index) + ".xml"
                self.new_voc_files[xml_filename] = {"folder":folder, "filename":filename, 
                    "path":path, "source":source, "size":size, "segmented":segmented,
                    "object":self.image_data_points[image_file]["object"]}

    def write_new_vocs(self):
        # This is where the objects listed in self.new_voc_files actually get written to their 
        # corresponding XML files
        for new_file in self.new_voc_files.keys():
            with open(new_file, "w") as out_file: 
                print("Write a voc file")
                print(self.new_voc_files[new_file])
                #TODO Actually write the file 
                #self.json_body has all the common voc info and newfile has the list of "Objects"



if __name__=='__main__':
    #TODO Loop through xmls
    infile="<something.xml>"
    outfolder = "<some output folder>"
    height=512
    width=512
    start_num=0
    ic = image_cropper()
    ic.crop(infile,outfolder,height,width,start_num)
    

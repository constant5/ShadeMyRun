from PIL import Image
import os
import json
import xmltodict
from pascal_voc_writer import Writer

class image_cropper:

    def __crop(self,infile,height,width):
        with Image.open(infile) as im:
            imgwidth, imgheight = im.size
            for i in range(imgheight//height):
                for j in range(imgwidth//width):
                    box = (j*width, i*height, (j+1)*width, (i+1)*height)
                    yield (box, im.crop(box))

    def crop(self,infile,outfolder,height,width,start_num):
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
    def __init__(self):
        self.json_body = None
        #self.image_tile_boxes[<image>] = <box encompased>
        self.image_tile_boxes = dict()
        self.image_data_points = dict()
        self.new_voc_files = dict()

    def __crop_image(self,infile,outfolder,height,width,start_number):
        ic = image_cropper()
        box_dict = ic.crop(infile,outfolder,height,width,start_num)
        return box_dict

    def __parse_voc_file(self,infile):
        with open(infile) as xml_file:
            data_dict = xmltodict.parse(xml_file.read())
            self.json_body = json.dumps(data_dict)

    def split_voc_and_images(self,xmlfile,outfolder,height,width,start_num):
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
        for new_file in self.new_voc_files.keys():
            with open(new_file, "w") as out_file: 
                print("Write a voc file")
                print(self.new_voc_files[new_file])
                #TODO Actually write the file 
                #self.json_body has all the common voc info and newfile has the list of "Objects"



if __name__=='__main__':
    #TODO: Loop through xml files
    infile="<something.xml>"
    outfolder = "<some output folder> "
    height=512
    width=512
    start_num=0
    
    ic = image_cropper()
    ic.crop(infile,outfolder,height,width,start_num)
    

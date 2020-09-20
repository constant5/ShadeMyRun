import json
import cv2
import os
import JsonToXML
import xml.etree.cElementTree as ET
import xml.dom.minidom

def json_to_pascal_voc(file_name, output_dir, image_dir):
    json_object_list = dict()
    with open(file_name, 'r') as my_file:
        print(my_file)
        json_text = my_file.read()
        json_text = json.loads(json_text)
        folder = image_dir.split("/")[-1]
        json_object_list["folder"] = folder

        # img_name = json_text['annotation']['path'].replace("E:\Widow CV Data\\", cwd)
        img_name = json_text['content'].split("\\")[-1] + ".png"
        json_object_list["filename"] = img_name

        path = image_dir + img_name
        json_object_list["path"] = path

        json_object_list["source"] = {"database":"Unknown"}

        im = cv2.imread(path)
        width, height, depth = im.shape
        size = {"width":width, "height":height, "depth":depth}
        json_object_list["size"] = size

        segmented = {"segmented":"0"}
        json_object_list["segmented"] = "0"

        json_object_list["object"] = []
        for bounding_box in json_text["annotation"]:
            #name = bounding_box["label"]
            name = "tree"
            pose = "Unspecified"
            trunkated = "0"
            difficult = "0"
            xmin = bounding_box["x_min"]
            ymin = bounding_box["y_min"]
            xmax = bounding_box["x_max"]
            ymax = bounding_box["y_max"]
            bndbox = {"bndbox":{"xmin":xmin,"ymin":ymin,"xmax":xmax,"ymax":ymax}}
            my_object = {"name":name, "pose":pose, "trunkated":trunkated, "difficult":difficult, "bndbox":bndbox}
            json_object_list["object"].append(my_object)


        return json.dumps(json_object_list)


# %%

#{"content": "maps\\CubComplex2009_401377N_12146256W", "annotation": [{"max_h": 37.92, "x_min": 188.41919438590773, "x_max": 182.49735873408764,
# "y_min": 2.290860966074602, "y_max": 7.265202913603464},

#
# def xml_list_to_json_file(xml_list, output_filename):
#     output_filename = output_filename
#     with open(output_filename, "w+") as output_file:
#         for xml_file in xml_list:
#             json = pascal_voc_to_json(xml_file)
#             output_file.write(str(json).replace("'", '"') + "\n")
#     return output_filename


img_folder = "/home/zac/ShadeMyRun/sample-20200916T181117Z-001/sample/maps/"
data_path = "/home/zac/ShadeMyRun/sample-20200916T181117Z-001/sample/labels/"
output_dir = "/home/zac/ShadeMyRun/VocFiles/"

filelist = []
for filename in os.listdir(data_path):
    print(filename)
    if filename.endswith("js"):
        filelist.append(data_path + filename)

for file in filelist:
    root = JsonToXML.fromText(json_to_pascal_voc(file, output_dir, img_folder), rootName="annotation")  # convert the file to XML and return the root node
    xmlData = ET.tostring(root, encoding='utf8', method='xml').decode()  # convert the XML data to string
    dom = xml.dom.minidom.parseString(xmlData)
    prettyXmlData = dom.toprettyxml()  # properly format the string of XML data
    print(prettyXmlData)  # print the formatted XML data
# print(len(filelist))
# print(xml_list_to_json_file(filelist, json_data_file))



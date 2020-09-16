# retrieves map images from arcgis server given a zipped shape file

# import packages

import json
import os
import subprocess
from zipfile import ZipFile
import pycrs
import shapefile as shp
from pyproj import Proj
import logging
import rasterio
import re
from lxml import html
import requests
import matplotlib.pyplot as plt
from PIL import Image
import numpy as np


class mapRetrieve():
    def __init__(self, in_folder='data',
                 out_folder='maps', label_folder='labels', log=False):
        # folder of zipped shapes
        self.in_folder = in_folder
        # folder for output shapes
        self.out_folder = out_folder
        # make output folder if none exists
        if not os.path.isdir(self.out_folder):
            os.mkdir(self.out_folder)
        # folder for json labels
        self.label_folder = label_folder
        # make label folder if none exists
        if not os.path.isdir(self.label_folder):
            os.mkdir(self.label_folder)


        # source data hosted on arcgis server
        self.src_file = 'http://server.arcgisonline.com/arcgis/'\
                        'rest/services/ESRI_Imagery_World_2D/'\
                        'MapServer?f=json&pretty=true'
        # a temp file to hold transformations
        self.temp_map = os.path.join(self.out_folder,'temp.tif')

        # enable or disable logging
        logger = logging.getLogger()
        if log:
            # turn on logging to get output from methods
            logger.setLevel(logging.INFO) 
        else:
            logger.setLevel(logging.WARNING)



    def load_shape(self, f_name: str):
        '''Get shape object and projection from a zip file. 

        Parameters
        ----------
        f_name : str
            the file name of a zip file containing an ESRI shape

        Returns
        -------
        shp.Shape
            a Shape object from the shapefile module
        str
            a string with the proj4 projection defintion of the shape
        '''
        # open the zip file
        zipshape = ZipFile(f_name)
        shape_name = re.split(r'/|\\+', f_name)[-1]
        shape_name = shape_name.split('.')[0]
        # print(shape_name)
        shape = shp.Reader(shp=zipshape.open(shape_name+'.shp'),
                           shx=zipshape.open(shape_name+'.shx'),
                           dbf=zipshape.open(shape_name+'.dbf'))

        # read the projection file
        prj = str(zipshape.open(shape_name+'.prj').readlines())[3:-1]
        url = 'https://spatialreference.org/ref/epsg/' + \
                prj.split('"')[1].replace('_','-').replace('-19','').lower() + '/'
        logging.info(f'\nGetting epsg from {url}')
        page = requests.get(url)
        tree = html.fromstring(page.content)
        epsg = tree.xpath('//h1/text()')[0]
        logging.info(f'Got {epsg}')
        # convert the prj format to proj4
        crs = pycrs.parse.from_esri_wkt(prj)
        proj4 = crs.to_proj4()
        logging.info(f'\nProj4 string decoded:\n {proj4}')
        return shape, proj4, epsg

    def get_bounds(self, shape, proj4):
        '''Get the bound of a shape object and project them into geocoordinates. 

        Parameters
        ----------
        shape : shp.Shape
            A Shape object from the shapefile module
        proj4 : str
            a string with the proj4 projection defintion of the shape

        Returns
        ----------
        list
            a list with the bounding box coordinates in the format, 
                [upper left x, upper left y, lower right x, lower right y]

        '''
        # get bounding box
        utm_extents = shape.bbox
        # print(utm_extents)

        # define projection object
        myProj = Proj(proj4)

        # project UTM to geocoordinates
        llx, lly = myProj(utm_extents[0], utm_extents[1], inverse=True)
        upx, upy = myProj(utm_extents[2], utm_extents[3], inverse=True)

        # note we have to do a conversion to get the bb in the right order for gdal
        extents = [llx, upy, upx, lly]
        logging.info(f'\nProjected extents:\n {extents}')
        return extents, utm_extents

    def get_map(self, extents, dst_file):
        '''Retrieve a map from given extents and save it.  

        Parameters
        ----------
        extents : list
            a list with the bounding box coordinates in the format, 
                [upper left x, upper left y, lower right x, lower right y]
        dst_file : str
            the name of the file to save the map to

        Returns
        ----------
        int
            the return code from the subprocess call

        '''

        # build option string for GDAL translate command
        # translate_option = f'-projwin {" ".join(map(str, extents))} ' \
        #                    f'-ot Byte ' \
        #                    f'-of PNG ' \
        #                    f'-co ZLEVEL=1 ' \
        #                    f'"{self.src_file}" ' \
        #                    f'{dst_file}'
        # build option string for GDAL translate command
        translate_option = f'-projwin {" ".join(map(str, extents))} ' \
                           f'-ot Byte ' \
                           f'-of GTiff ' \
                           f'-co COMPRESS=NONE ' \
                           f'-co BIGTIFF=IF_NEEDED ' \
                           f'"{self.src_file}" ' \
                           f'{dst_file}'

        # print(translate_option)

        # run command command as system process
        p_out = subprocess.run('gdal_translate ' + translate_option,
                               shell=True,
                               stdout=subprocess.PIPE,
                               stderr=subprocess.PIPE,
                               text=True)

        # display process outputs
        stdout = p_out.stdout
        logging.info(f'\nstdout:\n {stdout}')  # stdout = normal output
        stderr = p_out.stderr  # stderr = error output
        if stderr:
            logging.warning(f'\nsterr:\n {stderr}')

        # simply return return code for test function later
        rc = p_out.returncode
        logging.info(f'\nThe process returned with code: {rc}')
        
        return 
    
    def warp_map(self, src_file, dst_file, epsg):
        '''warps a tiff map in EPSPG:4326 to epsg specified. note that
           that the src_file is deleted before return.  

        Parameters
        ----------
        src_file : str
            the file location of the source map
        dst_file : str
            the file location of the destination map
        epsg : str
            the epsg code of the desired re-projection (ex. 'EPSG:2610')
        '''

        # build option string for GDAL warp command
        warp_option = f'-s_srs EPSG:4326 '\
                      f'-t_srs {epsg} '\
                      f'-r near '\
                      f'-of GTiff '\
                      f'-overwrite '\
                      f'{src_file} '\
                      f'{dst_file}'

        # run command command as system process
        p_out = subprocess.run('gdalwarp ' + warp_option,
                               shell=True,
                               stdout=subprocess.PIPE,
                               stderr=subprocess.PIPE,
                               text=True)

        # display process outputs
        stdout = p_out.stdout
        logging.info(f'\nstdout:\n {stdout}')  # stdout = normal output
        stderr = p_out.stderr  # stderr = error output
        if stderr:
            logging.warning(f'\nsterr:\n {stderr}')

        # delete temp_map
        os.remove(src_file)

        # simply return return code for test function later
        rc = p_out.returncode
        logging.info(f'\nThe process returned with code: {rc}')
        
        return
    
    def png_map(self, src_file, dst_file):
        '''convert a tiff map to a png map. note that that src_file is
           deleted before return.  

        Parameters
        ----------
        src_file : str
            the file location of the source map
        dst_file : str
            the file location of the destination map
        '''

        # build option string for GDAL translate command
        translate_option = f'-of PNG ' \
                           f'-co ZLEVEL=1 ' \
                           f'"{src_file}" ' \
                           f'{dst_file}'

        # print(translate_option)

        # run command command as system process
        p_out = subprocess.run('gdal_translate ' + translate_option,
                               shell=True,
                               stdout=subprocess.PIPE,
                               stderr=subprocess.PIPE,
                               text=True)

        # display process outputs
        stdout = p_out.stdout
        logging.info(f'\nstdout:\n {stdout}')  # stdout = normal output
        stderr = p_out.stderr  # stderr = error output
        if stderr:
            logging.warning(f'\nsterr:\n {stderr}')

        # delete temp_map
        os.remove(src_file)

        # simply return return code for test function later
        rc = p_out.returncode
        logging.info(f'\nThe process returned with code: {rc}')
        
        return 

    def save_map(self, zf, validate=False):
        '''From a given shape file, retrieve a hig-res map from a server
        source with same extents of the and save it locally to ./maps/   

        Parameters
        ----------
        zf : zipfile.ZipFile
            a zip file containing an ESRI shape object

        Returns
        ----------
        rc
            the return code from the subprocess call

        '''

        # shape_name = zf.split('/')[-1].split('.')[0]
        shape_name = re.split(r'/|\\+', zf)[-1].split('.')[0]
        shape, proj4, epsg = self.load_shape(zf)
        extents, _ = self.get_bounds(shape, proj4)
        dst_file = os.path.join(self.out_folder,f'{shape_name}')
        self.get_map(extents, dst_file=self.temp_map)
        self.warp_map(src_file=self.temp_map, dst_file=dst_file+'temp.tif', epsg=epsg)
        self.png_map(src_file=dst_file+'temp.tif', dst_file=dst_file+'.png')

        src = rasterio.open(dst_file+'.png')

        json_file = self.shape_to_json(shape, src.transform, dst_file)

        self.save_json(json_file, os.path.join(self.label_folder,shape_name+'.js'))

        if validate:
            self.png_print(png_dst_file=dst_file+'.png', 
                           label_file=os.path.join(self.label_folder,shape_name+'.js'))
        return

    def shape_to_json(self, shapes, transform, f_name='test.js'):
        '''Convert a shape object to simplified bounding boxes and 
           store in json structured dict   

        Parameters
        ----------
        shape : shapefile.Shape
            a shape object containing polygons 

        Returns
        ----------
        dict
            the bounding box details in dictionary form

        '''
        x_offset = 0
        y_offset = 0
        x_scale = 1
        y_scale = 1
        if not isinstance(transform, str):
            x_offset = transform.c
            y_offset = transform.f
            x_scale = transform.a
            y_scale = transform.e
        else:
            print("SOMETHING WENT WRONG WITH TRANSFORM OBJECT")
            print(transform)
            exit()
        json_file = {'content': f_name, 'annotation': []}
        for shape in shapes.shapeRecords():
            maxx, maxy, minx, miny = shape.shape.bbox
            features = {}
            height = shape.record.max_h
            # only get bboxses for trees greater than 30 ft(?)
            if height > 30: 
                features['max_h'] = height

                features['x_min'] = (minx - x_offset) / x_scale
                features['x_max'] = (maxx - x_offset) / x_scale
                features['y_min'] = (miny - y_offset) / y_scale
                features['y_max'] = (maxy - y_offset) / y_scale

                
                json_file['annotation'].append(features)
        return json_file

    def save_json(self, json_file, dst_file):
        '''Save a json structured dictionary to a file   

        Parameters
        ----------
        json_file : dict
            a dictionary to save to json 

        dst_file : str
            the filename destination to save the dictionary
        '''
        with open(dst_file, 'w') as output_file:
            json.dump(json_file, output_file)
            #json.dump(json_file, output_file, indent=2)
        return

    def png_print(self, png_dst_file,label_file):
        ''' display a png file with labels
        
        Parameters
        ----------
        png_dst_file : str
            a file location of a png file
        label_file : str
            a file location of the associated label file
        '''
        with open(label_file) as json_file:
            labels = json.load(json_file)

        # a little helper func
        def get_png_size(f_name):
            with Image.open(f_name) as img:
                im = np.array(img)
                logging.info(f'\nimage shape: {im.shape}')
            return im.shape


        def plot_labels(labels):
            for item in labels['annotation']:
                h = item['max_h']
                s_minx = item['x_min']
                s_maxx = item['x_max']
                s_miny = item['y_min']
                s_maxy = item['y_max']
                x = [s_minx, s_minx, s_maxx, s_maxx, s_minx]
                y = [s_miny, s_maxy, s_maxy, s_miny, s_miny]
                plt.plot(x,y, linewidth=5)

        def plot_png(png_dst_file):
            png_size = get_png_size(png_dst_file)[:2]
            fig = plt.figure(figsize=(png_size[1]/20,png_size[0]/20))
            img = Image.open(png_dst_file)
            plt.imshow(img)

        plot_png(png_dst_file)
        plot_labels(labels)
        plt.show()
         
        return

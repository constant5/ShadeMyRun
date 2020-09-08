# retrieves map images from arcgis server given a zipped shape file

# import packages
import pandas 
import numpy
import gdal
import ee
import shapefile as shp
from glob import glob
from zipfile import ZipFile
from pyproj import Proj, transform
import os
import subprocess
import pycrs
import logging
import unittest

class mapRetrieve():
    def __init__(self, in_folder='data/', out_folder='maps/'):
        # folder of zipped shapes
        self.in_folder = in_folder
        # folder for output shapes
        self.out_folder = out_folder
        # make output folder if none exists
        if not os.path.isdir(self.out_folder):
            os.mkdir(self.out_folder)
        # source data hosted on arcgis server
        self.src_file = 'http://server.arcgisonline.com/arcgis/rest/services/ESRI_Imagery_World_2D/MapServer?f=json&pretty=true'

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
        
        # read the shape file
        shape_name = f_name.split('\\')[1].split('.')[0]
        shape = shp.Reader(shp=zipshape.open(shape_name+'.shp'),
                           shx=zipshape.open(shape_name+'.shx'),
                           dbf=zipshape.open(shape_name+'.dbf'))
        
        # read the projection file
        prj = str(zipshape.open(shape_name+'.prj').readlines())[3:-1]
        
        # convert the prj format to proj4
        crs = pycrs.parse.from_esri_wkt(prj)
        proj4 = crs.to_proj4() 
        logging.info(f'\nProj4 string decoded:\n {proj4}')
        return shape, proj4

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
        
        # define projection object
        myProj = Proj(proj4)

        # project UTM to geocoordinates
        llx, lly = myProj(utm_extents[0], utm_extents[1], inverse=True)
        upx, upy = myProj(utm_extents[2], utm_extents[3], inverse=True)
        
        # note we have to do a conversion to get the bb in the right order for gdal
        extents = [llx, upy, upx, lly]
        logging.info(f'\nProjected extents:\n {extents}')
        return extents


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
            the return code from the subprocees call

        '''

        # build option string for GDAL translate command
        translate_option = f'-projwin {" ".join(map(str, extents))} '\
                           f'-ot Byte '\
                           f'-of GTiff '\
                           f'-co COMPRESS=NONE '\
                           f'-co BIGTIFF=IF_NEEDED '\
                           f'{self.src_file} '\
                           f'{dst_file}'

        # print(translate_option)

        # run command command as system process 
        p_out = subprocess.run('gdal_translate ' + translate_option, 
                                stdout=subprocess.PIPE,
                                stderr=subprocess.PIPE,
                                text=True)
        
        # display procees outputs
        stdout = p_out.stdout
        logging.info(f'\nstdout:\n {stdout}') # stdout = normal output
        stderr = p_out.stderr # stderr = error output
        if stderr:
            logging.warning(f'\nsterr:\n {stderr}')
        
        # simply return return code for test function later
        return p_out.returncode

    def get_maps(self, zf):
        '''From a given shape file, retrieve a hig-res map from a server
        source with same extents of the and save it locally to ./maps/   

        Parameters
        ----------
        zf : zipfile.ZipFile
            a zip file containing an ESRI shape object

        Returns
        ----------
        rc
            the return code from the subprocees call

        '''

        shape_name = zf.split('\\')[1].split('.')[0]
        shape, proj4 = self.load_shape(zf)
        extents = self.get_bounds(shape, proj4)
        dst_file = f'{self.out_folder}{shape_name}.tif'
        rc = self.get_map(extents, dst_file)
        logging.info(f'\nThe process returned with code: {rc}')
        return rc 







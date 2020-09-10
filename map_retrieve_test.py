from map_retrieve import mapRetrieve
import unittest
import logging
import os

class TestRetrieveMap(unittest.TestCase):
    """
    Testing mapRetrieval class methods
    """
    @classmethod
    def setUpClass(self):
        self.mr = mapRetrieve(in_folder='data/', out_folder='maps/')
        self.f_name = 'data\\Taliaferro2013_3992854N_12308761W.zip'
        self.in_folder='data/'
        self.out_folder='maps/'
        self.dst_file = 'data/test_clip.tif'


    def test_load_shape(self):
        """
        Testing load_shape method.
        """
        _, proj4 = self.mr.load_shape(self.f_name)
        proj4_expect = '+proj=utm +datum=NAD83 +ellps=GRS80'\
                        ' +a=6378137.0 +rf=298.257222101'\
                        ' +pm=0 +lat_0=0.0 +lon_0=-123.0'\
                        ' +x_0=500000.0 +y_0=0.0 +units=m'\
                        ' +axis=enu +no_defs'
        self.assertEqual(proj4, proj4_expect)
    
    def test_get_extents(self):
        """
        Testing get_extents method.
        """
        shape, proj4 = self.mr.load_shape(self.f_name)
        extents = self.mr.get_bounds(shape, proj4)
        self.assertEqual(extents,
                         [-123.08760652043246, 
                         39.9285503651239, 
                         -123.07501000231119, 
                         39.924924051103275])
        
    def test_get_map(self):
        """
        Testing get_map method.
        """
        shape, proj4 = self.mr.load_shape(self.f_name)
        extents = self.mr.get_bounds(shape, proj4)
        self.mr.get_map(extents, self.dst_file)
        self.assertTrue(os.path.exists(self.dst_file))
        os.remove(self.dst_file)

    def test_save_map(self):
        """
        Testing save_map method (not completed)
        """
        # TODO: Write test to get multiple map images 
        # mr.save_map(f_name)
        pass 

    def test_save_json(self):
        shape, _ = self.mr.load_shape(self.f_name)
        json_file = self.mr.shape_to_json(shape)
        dst_file = 'test.ds'
        self.mr.save_json(json_file, dst_file)
        self.assertTrue(os.path.exists(dst_file))
        os.remove(dst_file)
        

if __name__ == "__main__":
    # test
    logging.basicConfig(level=logging.INFO)
    unittest.main()
    logging.basicConfig(level=logging.WARNING)
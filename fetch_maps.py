import os
from map_retrieve import mapRetrieve
from glob import glob

# create the mapRetrieve object
mr = mapRetrieve()

zip_files = glob('/media/zac/Seagate Portable Drive/orders/f06d9ed2c630d7ad6ecfd53ecda4d412/CMS_LiDAR_AGB_California/data/*.zip')
# for each zip file run the save_map method
count = 10000
for zf in zip_files:
    count = count -1
    if count > 0:
        print(zf)
        print(count)
        mr.save_map(zf)
    else:
        continue

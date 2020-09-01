## Shade My Run 
#### A Project Proposal for CSCE 5214 
Group Participants | Contact Information 
------------------ | -------------------
Constant Marks |
Daniel Mata | 
Zachary O\'Brien |
Jason Gillette | JasonGillette@my.unt.edu

**Executive Summary**

The purpose of *Shade My Run* is to assist runners in identifying routes with ample shade provided by tree cover. This project will use a segment of LiDAR imagery data to successfully train a model to identify tree cover within more widely available sattelite imagery data. With the simple entry of a turn-around point, the user will gain a shaded route on low-volume roadways, and route details such as distance and elevation. 

**Project Abstract**

**Inputs:** The data being utilized in the project is *LiDAR-Derived Aboveground Biomass and Uncertainty for California Forests, 2005-2014* from the Oak Ridge National Laboratory (ORNL) Distributed Active Archive Center (DAAC). This dataset provides estimates of aboveground biomass and spatially explicit uncertainty from 53 airborne LiDAR surveys of locations throughout California between 2005 and 2014. Additional data being utilized includes sattelite imagery from...

**Project Design:** In order to...\*Jupyter notebooks, AWS, etc.\*

**Milestones**
1. MVP: Train a model (using DAAC Lidar data) to detect tree cover from a satellite image
2. Utilize the Google Earth Engine to pull dynamic satellite images for inference 
3. Utilize Google Maps APIs to determine options for running routes, then use this data to create bounds for the inference
4. Use turn by turn directions from the Google Maps API to break the route into segments that can individually be run against for tree coverage
5. For each route, use the model to give it a "Shade coverage" percentage
6. Implement a basic interface for inputing route start/end/waypoints (% shade will be shown next to the route options) 
7. Display route in map form to the user
8. Utilize "End" has a halfway point and return the user to their starting location (possibly via a different route) 


**Resources**
* Inspiration:[Mapping All Trees With Machine Learning](https://medium.com/descarteslabs-team/descartes-labs-urban-trees-tree-canopy-mapping-3b6c85c5c9cc)
* Data:[LiDAR-Derived Aboveground Biomass and Uncertainty for California Forests, 2005-2014](https://daac.ornl.gov/cgi-bin/dsviewer.pl?ds_id=1537)
* Data:[LiDAR Data User Guide](https://daac.ornl.gov/CMS/guides/CMS_LiDAR_AGB_California.html)

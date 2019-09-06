"""
Send strain calculation to the right driver. 
"""

import sys
import configure_functions
import input_manager
import output_manager
import delaunay_strain
import hammond_strain
import gpsgridder_strain
import visr_strain
import spline_strain
import ND_interp_strain
import strain_tensor_toolbox



# The types of driver functions. 
def driver_1d(strain_method):
	[MyParams] = configure_functions.configure(strain_method);
	[myVelfield] = input_manager.inputs(MyParams);
	[xdata, ydata, polygon_vertices, rot, e1, e2, v00, v01, v10, v11] = compute_dict[strain_method](myVelfield, MyParams);
	[I2nd, max_shear, dilatation, azimuth] = strain_tensor_toolbox.compute_derived_quantities(e1, e2, v00, v01, v10, v11);
	output_manager.outputs_1d(xdata, ydata, polygon_vertices, I2nd, max_shear, rot, e1, e2, v00, v01, v10, v11, dilatation, azimuth, myVelfield, MyParams);
	return;

def driver_2d(strain_method):
	[MyParams] = configure_functions.configure(strain_method);
	[myVelfield] = input_manager.inputs(MyParams);
	[xdata, ydata, rot, e1, e2, v00, v01, v10, v11] = compute_dict[strain_method](myVelfield, MyParams);
	[I2nd, max_shear, dilatation, azimuth] = strain_tensor_toolbox.compute_derived_quantities(e1, e2, v00, v01, v10, v11);
	output_manager.outputs_2d(xdata, ydata, I2nd, max_shear, rot, e1, e2, v00, v01, v10, v11, dilatation, myVelfield, MyParams);	
	return;





# The method look-up table
# Are we producing gridded interpolated data, or static polygons?
driver_dict={
	"delaunay":driver_1d, 
	"hammond":driver_1d,
	"ND_interp":driver_2d,
	"spline":driver_2d,
	"gpsgridder":driver_2d,
	"visr": driver_2d };

# Where does the compute method live? 
compute_dict={
	"delaunay":delaunay_strain.compute, 
	"hammond":hammond_strain.compute,
	"ND_interp":ND_interp_strain.compute,
	"spline":spline_strain.compute,
	"gpsgridder":gpsgridder_strain.compute,
	"visr":visr_strain.compute };


def method_directory(strain_method):
	# Call the main function itself. 
	driver_dict[strain_method](strain_method);
	return; 




# The output manager for GPS Strain analysis. 
# ----------------- OUTPUTS -------------------------



import numpy as np 
import subprocess, sys, os
import gps_input_functions
import netcdf_functions
import strain_tensor_toolbox


def outputs_2d(xdata, ydata, I2nd, max_shear, rot, e1, e2, v00, v01, v10, v11, dilatation, myVelfield, MyParams):
	print("Writing 2d outputs:");
	outfile=open(MyParams.outdir+"tempgps.txt",'w');
	for i in range(len(myVelfield.n)):
		outfile.write("%f %f %f %f %f %f 0.0\n" % (myVelfield.elon[i], myVelfield.nlat[i], myVelfield.e[i], myVelfield.n[i], myVelfield.se[i], myVelfield.sn[i]) );
	outfile.close();
	azimuth = strain_tensor_toolbox.max_shortening_azimuth(e1, e2, v00, v01, v10, v11)
	netcdf_functions.produce_output_netcdf(xdata, ydata, azimuth, 'degrees', MyParams.outdir+'azimuth.nc');
	netcdf_functions.produce_output_netcdf(xdata, ydata, I2nd, 'per yr', MyParams.outdir+'I2nd.nc');
	netcdf_functions.flip_if_necessary(MyParams.outdir+'I2nd.nc');
	netcdf_functions.produce_output_netcdf(xdata, ydata, rot, 'per yr', MyParams.outdir+'rot.nc');
	netcdf_functions.flip_if_necessary(MyParams.outdir+'rot.nc');
	netcdf_functions.produce_output_netcdf(xdata, ydata, dilatation, 'per yr', MyParams.outdir+'dila.nc');
	netcdf_functions.flip_if_necessary(MyParams.outdir+'dila.nc');
	netcdf_functions.produce_output_netcdf(xdata, ydata, max_shear, 'per yr', MyParams.outdir+'max_shear.nc');
	netcdf_functions.flip_if_necessary(MyParams.outdir+'max_shear.nc');
	print("Max I2: %f " % (np.amax(I2nd)));
	print("Max rot: %f " % (np.amax(rot)));
	print("Min rot: %f " % (np.amin(rot)));
	write_grid_eigenvectors(xdata, ydata, e1, e2, v00, v01, v10, v11, MyParams);
	gmt_file=open(MyParams.outdir+"run_gmt.gmt", 'w');
	gmt_file.write("../../../"+MyParams.gmtfile+" "+MyParams.map_range+"\n");
	gmt_file.close();
	upfile=open(MyParams.outdir+"uplift.txt", 'w');
	for i in range(len(myVelfield.n)):
		upfile.write("%f %f %f \n" % (myVelfield.elon[i], myVelfield.nlat[i], myVelfield.u[i]));
	upfile.close();
	print("../../../"+MyParams.gmtfile+" "+MyParams.map_range);
	return;

def write_grid_eigenvectors(xdata, ydata, w1, w2, v00, v01, v10, v11, MyParams):
	# Need eigs_interval and outdir from MyParams. 
	positive_file=open(MyParams.outdir+"positive_eigs.txt",'w');
	negative_file=open(MyParams.outdir+"negative_eigs.txt",'w');
	if MyParams.strain_method=='visr':
		eigs_dec=8;
	elif MyParams.strain_method=='gpsgridder':
		eigs_dec=12;
	elif MyParams.strain_method=='spline':
		eigs_dec=8;
	elif MyParams.strain_method=='ND_interp':
		eigs_dec=12;
	else:
		print("Error! strain method not recognized for eigenvector plotting.");

	do_not_print_value=200;
	overmax_scale=200;

	for j in range(len(ydata)):
		for k in range(len(xdata)):
			if np.mod(j,eigs_dec)==0 and np.mod(k,eigs_dec)==0:
				if w1[j][k]>0:
					scale=w1[j][k];
					if abs(scale)>do_not_print_value:
						scale=overmax_scale;
					positive_file.write("%s %s %s %s 0 0 0\n" % (xdata[k], ydata[j], v00[j][k]*scale, v10[j][k]*scale) );
					positive_file.write("%s %s %s %s 0 0 0\n" % (xdata[k], ydata[j], -v00[j][k]*scale, -v10[j][k]*scale) );
				if w1[j][k]<0:
					scale=w1[j][k];
					if abs(scale)>do_not_print_value:
						scale=overmax_scale;					
					negative_file.write("%s %s %s %s 0 0 0\n" % (xdata[k], ydata[j], v00[j][k]*scale, v10[j][k]*scale) );
					negative_file.write("%s %s %s %s 0 0 0\n" % (xdata[k], ydata[j], -v00[j][k]*scale, -v10[j][k]*scale) );
				if w2[j][k]>0:
					scale=w2[j][k];
					if abs(scale)>do_not_print_value:
						scale=overmax_scale;
					positive_file.write("%s %s %s %s 0 0 0\n" % (xdata[k], ydata[j], v01[j][k]*scale, v11[j][k]*scale) );
					positive_file.write("%s %s %s %s 0 0 0\n" % (xdata[k], ydata[j], -v01[j][k]*scale, -v11[j][k]*scale) );
				if w2[j][k]<0:
					scale=w2[j][k];
					if abs(scale)>do_not_print_value:
						scale=overmax_scale;
					negative_file.write("%s %s %s %s 0 0 0\n" % (xdata[k], ydata[j], v01[j][k]*scale, v11[j][k]*scale) );
					negative_file.write("%s %s %s %s 0 0 0\n" % (xdata[k], ydata[j], -v01[j][k]*scale, -v11[j][k]*scale) );
	positive_file.close();
	negative_file.close();

	return;



def outputs_1d(xcentroid, ycentroid, polygon_vertices, I2nd, max_shear, rot, e1, e2, v00, v01, v10, v11, dilatation, azimuth, myVelfield, MyParams):
	print("Writing 1d outputs:");

	rotfile=open(MyParams.outdir+"rotation.txt",'w');
	I2ndfile=open(MyParams.outdir+"I2nd.txt",'w');
	Dfile=open(MyParams.outdir+"Dilatation.txt",'w');
	maxfile=open(MyParams.outdir+"max_shear.txt",'w');
	positive_file=open(MyParams.outdir+"positive_eigs.txt",'w');
	negative_file=open(MyParams.outdir+"negative_eigs.txt",'w');
	gmt_file=open(MyParams.outdir+"run_gmt.sh", 'w');
	azfile=open(MyParams.outdir+"azimuth.txt", 'w');
	upfile=open(MyParams.outdir+"uplift.txt", 'w');

	outfile=open(MyParams.outdir+"tempgps.txt",'w');
	for i in range(len(myVelfield.n)):
		outfile.write("%f %f %f %f %f %f 0.0\n" % (myVelfield.elon[i], myVelfield.nlat[i], myVelfield.e[i], myVelfield.n[i], myVelfield.se[i], myVelfield.sn[i]) );
	outfile.close();

		# write uplift file
	for i in range(len(myVelfield.n)):
		upfile.write("%f %f %f \n" % (myVelfield.elon[i], myVelfield.nlat[i], myVelfield.u[i]));
	upfile.close();

	for i in range(len(I2nd)):
		# Write the triangle's rotation
		rotfile.write("> -Z"+str(rot[i])+"\n");
		rotfile.write(str(polygon_vertices[i,0,0])+" "+str(polygon_vertices[i,0,1])+"\n");
		rotfile.write(str(polygon_vertices[i,1,0])+" "+str(polygon_vertices[i,1,1])+"\n");
		rotfile.write(str(polygon_vertices[i,2,0])+" "+str(polygon_vertices[i,2,1])+"\n");

		# Write the triangle's I2
		I2ndfile.write("> -Z"+str(I2nd[i])+"\n");
		I2ndfile.write(str(polygon_vertices[i,0,0])+" "+str(polygon_vertices[i,0,1])+"\n");
		I2ndfile.write(str(polygon_vertices[i,1,0])+" "+str(polygon_vertices[i,1,1])+"\n");
		I2ndfile.write(str(polygon_vertices[i,2,0])+" "+str(polygon_vertices[i,2,1])+"\n");
		
		# Write the dilatation
		Dfile.write("> -Z"+str(dilatation[i])+"\n"); 
		Dfile.write(str(polygon_vertices[i,0,0])+" "+str(polygon_vertices[i,0,1])+"\n");
		Dfile.write(str(polygon_vertices[i,1,0])+" "+str(polygon_vertices[i,1,1])+"\n");
		Dfile.write(str(polygon_vertices[i,2,0])+" "+str(polygon_vertices[i,2,1])+"\n");

		# Write the max shear
		maxfile.write("> -Z"+str(max_shear[i])+"\n"); 
		maxfile.write(str(polygon_vertices[i,0,0])+" "+str(polygon_vertices[i,0,1])+"\n");
		maxfile.write(str(polygon_vertices[i,1,0])+" "+str(polygon_vertices[i,1,1])+"\n");
		maxfile.write(str(polygon_vertices[i,2,0])+" "+str(polygon_vertices[i,2,1])+"\n");

		# Write the azimuth
		azfile.write("> -Z"+str(azimuth[i])+"\n"); 
		azfile.write(str(polygon_vertices[i,0,0])+" "+str(polygon_vertices[i,0,1])+"\n");
		azfile.write(str(polygon_vertices[i,1,0])+" "+str(polygon_vertices[i,1,1])+"\n");
		azfile.write(str(polygon_vertices[i,2,0])+" "+str(polygon_vertices[i,2,1])+"\n");

		# Write the eigenvectors and eigenvalues
		write_single_eigenvector(positive_file, negative_file, e1[i], v00[i], v10[i], xcentroid[i], ycentroid[i]);
		write_single_eigenvector(positive_file, negative_file, e2[i], v01[i], v11[i], xcentroid[i], ycentroid[i]);
	
	gmt_file.write("../../../"+MyParams.gmtfile+" "+MyParams.map_range+"\n")

	print("Max I2: %f " % (max(I2nd)));
	print("Max rot: %f " % (max(rot)));
	print("Min rot: %f " % (min(rot)));

	rotfile.close();
	I2ndfile.close();
	Dfile.close();
	maxfile.close();
	positive_file.close();
	negative_file.close();
	gmt_file.close();
	azfile.close();

	return;



def write_single_eigenvector(positive_file, negative_file, e, v0, v1, x, y):
	# e = eigenvalue, [v0, v1] = eigenvector. 
	# Writes a single eigenvector eigenvalue pair. 
	# Also has functionality to saturate eigenvectors so they don't blow up. 
	overall_max=40.0;
	scale=0.4*e;

	vx=v0*scale;
	vy=v1*scale;
	if np.sqrt(vx*vx+vy*vy)>overall_max:
		scale=scale*(overall_max/np.sqrt(vx*vx+vy*vy))
		vx=v0*scale;
		vy=v1*scale;

	if e>0:
		positive_file.write("%s %s %s %s 0 0 0\n" % (x, y, vx, vy ));
		positive_file.write("%s %s %s %s 0 0 0\n" % (x, y, -vx, -vy ));
	else:	
		negative_file.write("%s %s %s %s 0 0 0\n" % (x, y, vx, vy ));
		negative_file.write("%s %s %s %s 0 0 0\n" % (x, y, -vx, -vy ));
	return;



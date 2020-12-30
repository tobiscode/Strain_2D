"""
May 2018
Take a set of velocities, establish delaunay triangles, 
solve a linear inversion problem for the components of the velocity gradient tensor
at the centroid of each triangle. 
The strain rate tensor and the rotation tensor can be readily computed 
from the symmetric and anti-symmetric parts of the velocity gradient tensor. 
Plot the outputs. 

Following a technique learned in Brad Hagar's geodynamics class, and 
modeled off of advice from 2007 Journal of Geodynamcis paper:
ftp://ftp.ingv.it/pub/salvatore.barba/RevEu/Cai_StrainBIFROST_2007.pdf
"""

import numpy as np
from scipy.spatial import Delaunay
from numpy.linalg import inv, det
import strain_tensor_toolbox
import output_manager


# ----------------- COMPUTE -------------------------
def compute(myVelfield, myParams):
	print("------------------------------\nComputing strain via Delaunay method on a flat earth.");
	[xcentroid, ycentroid, triangle_vertices, rot, e1, e2, v00, v01, v10, v11] = compute_with_delaunay_polygons(myVelfield);

	# Here we will output convenient things on polygons, since it's intuitive for the user.
	[I2nd, max_shear, dilatation, azimuth] = strain_tensor_toolbox.compute_derived_quantities(e1, e2, v00, v01, v10, v11);
	output_manager.outputs_1d(xcentroid, ycentroid, triangle_vertices, I2nd, max_shear, rot, e1, e2, v00, v01, v10, v11, dilatation, azimuth, myVelfield, myParams);
	return [xcentroid, ycentroid, triangle_vertices, rot, e1, e2, v00, v01, v10, v11];


def compute_with_delaunay_polygons(myVelfield):

	print("Computing strain via delaunay method.");
	elon = [x.elon for x in myVelfield];
	nlat = [x.nlat for x in myVelfield];
	e = [x.e for x in myVelfield];
	n = [x.n for x in myVelfield];
	se = [x.se for x in myVelfield];
	sn = [x.sn for x in myVelfield];
	z = np.array([elon, nlat]);
	z = z.T;
	tri=Delaunay(z);

	triangle_vertices = z[tri.simplices];
	trishape = np.shape(triangle_vertices);  # 516 x 3 x 2, for example

	# We are going to solve for the velocity gradient tensor at the centroid of each triangle. 
	centroids=[];
	for i in range(trishape[0]):
		xcor_mean = np.mean([triangle_vertices[i,0,0],triangle_vertices[i,1,0],triangle_vertices[i,2,0]]);
		ycor_mean = np.mean([triangle_vertices[i,0,1],triangle_vertices[i,1,1],triangle_vertices[i,2,1]]);
		centroids.append([xcor_mean,ycor_mean]);
	xcentroid=[x[0] for x in centroids];
	ycentroid=[x[1] for x in centroids];


	# Initialize arrays.
	rot=[];
	e1=[]; # eigenvalues
	e2=[];
	v00=[];  # eigenvectors
	v01=[];
	v10=[];
	v11=[];


	# for each triangle:
	for i in range(trishape[0]):

		# Get the velocities of each vertex (VE1, VN1, VE2, VN2, VE3, VN3)
		# Get velocities for Vertex 1 (triangle_vertices[i,0,0] and triangle_vertices[i,0,1])
		xindex1 = np.where(elon==triangle_vertices[i,0,0])
		yindex1 = np.where(nlat==triangle_vertices[i,0,1])
		index1=np.intersect1d(xindex1,yindex1);
		xindex2 = np.where(elon==triangle_vertices[i,1,0])
		yindex2 = np.where(nlat==triangle_vertices[i,1,1])
		index2=np.intersect1d(xindex2,yindex2);
		xindex3 = np.where(elon==triangle_vertices[i,2,0])
		yindex3 = np.where(nlat==triangle_vertices[i,2,1])
		index3=np.intersect1d(xindex3,yindex3);

		VE1=e[index1[0]]; VN1=n[index1[0]];
		VE2=e[index2[0]]; VN2=n[index2[0]];
		VE3=e[index3[0]]; VN3=n[index3[0]];
		obs_vel = np.array([[VE1],[VN1],[VE2],[VN2],[VE3],[VN3]]);

		# Get the distance between centroid and vertex (in km)
		dE1 = (triangle_vertices[i,0,0]-xcentroid[i])*111.0*np.cos(np.deg2rad(ycentroid[i]));
		dE2 = (triangle_vertices[i,1,0]-xcentroid[i])*111.0*np.cos(np.deg2rad(ycentroid[i]));
		dE3 = (triangle_vertices[i,2,0]-xcentroid[i])*111.0*np.cos(np.deg2rad(ycentroid[i]));
		dN1 = (triangle_vertices[i,0,1]-ycentroid[i])*111.0;
		dN2 = (triangle_vertices[i,1,1]-ycentroid[i])*111.0;
		dN3 = (triangle_vertices[i,2,1]-ycentroid[i])*111.0;

		Design_Matrix = np.array([[1,0,dE1,dN1,0,0],[0,1,0,0,dE1,dN1],[1,0,dE2,dN2,0,0],[0,1,0,0,dE2,dN2],[1,0,dE3,dN3,0,0],[0,1,0,0,dE3,dN3]]);

		# Invert to get the components of the velocity gradient tensor. 
		DMinv = inv(Design_Matrix);
		vel_grad = np.dot(DMinv, obs_vel);  # this is the money step. 
		VE_centroid=vel_grad[0][0];
		VN_centroid=vel_grad[1][0];
		dVEdE=vel_grad[2][0];
		dVEdN=vel_grad[3][0];
		dVNdE=vel_grad[4][0];
		dVNdN=vel_grad[5][0];


		# The components that are easily computed
		[exx, exy, eyy, rotation] = strain_tensor_toolbox.compute_strain_components_from_dx(dVEdE, dVNdE, dVEdN, dVNdN);

		# # Compute a number of values based on tensor properties. 
		[e11, e22, v] = strain_tensor_toolbox.eigenvector_eigenvalue(exx, exy, eyy);

		e1.append(e11);
		e2.append(e22);
		rot.append(abs(rotation));
		v00.append(v[0][0]);
		v10.append(v[1][0]);
		v01.append(v[0][1]);
		v11.append(v[1][1]);

	print("Success computing strain via delaunay flat-earth method.\n");


	return [xcentroid, ycentroid, triangle_vertices, rot, e1, e2, v00, v01, v10, v11];





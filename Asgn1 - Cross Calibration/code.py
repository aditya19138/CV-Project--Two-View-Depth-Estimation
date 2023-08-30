# -*- coding: utf-8 -*-
"""CV_asgn2.py

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1YwgLc1HP7SlzRiXGrPut-458Kt_UkBXM
"""

import cv2
import numpy as np
import os
import glob
from google.colab.patches import cv2_imshow
import matplotlib.pyplot as plt

"""# Q1"""

# Defining the dimensions of checkerboard
CHECKERBOARD = (7,7)
criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 30, 0.001)
 
# Creating vector to store vectors of 3D points for each checkerboard image
objpoints = []
# Creating vector to store vectors of 2D points for each checkerboard image
imgpoints = [] 
 
 
# Defining the world coordinates for 3D points
objp = np.zeros((CHECKERBOARD[0] * CHECKERBOARD[1], 3), np.float32)
objp[:,:2] = np.mgrid[0:CHECKERBOARD[0], 0:CHECKERBOARD[1]].T.reshape(-1, 2)

directory_path = '/content/drive/MyDrive/CV_Asgn1/images'
directory_files = os.listdir(directory_path)

for fname in directory_files:
  img = cv2.imread(directory_path+"/"+fname)
  img = cv2.resize(img,(800,500))
  gray = cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)
  # Find the chess board corners
  # If desired number of corners are found in the image then ret = true
  ret, corners = cv2.findChessboardCorners(gray, CHECKERBOARD,None)
  if ret == True:
    objpoints.append(objp)
    # refining pixel coordinates for given 2d points.
    corners2 = cv2.cornerSubPix(gray, corners, (11,11),(-1,-1), criteria)
    
    imgpoints.append(corners2)

    # Draw and display the corners
    img = cv2.drawChessboardCorners(img, CHECKERBOARD, corners2, ret)
    print(fname)
    cv2_imshow(img)
    cv2.waitKey(0)

cv2.destroyAllWindows()

ret, mtx, dist, rvecs, tvecs = cv2.calibrateCamera(objpoints, imgpoints, gray.shape[::-1], None, None)

R = []
for i in range(25):
  r,_=cv2.Rodrigues(rvecs[i])
  R.append(r)

dist.shape

# save all the arrays
path= "/content/drive/MyDrive/CV_Asgn1/Q1_Matrices/"

np.save(path+'imgpoints',np.array(imgpoints))
np.save(path+'objpoints',np.array(objpoints))
np.save(path+'distortion_coeff',dist)
np.save(path+'rotation_vectors',rvecs)
np.save(path+'translation_vectors',tvecs)
np.save(path+'camera_matrix',mtx)
np.save(path+'roation matrices',np.array(R))

"""## Q1 c)"""

for i,fname in enumerate(directory_files):
  if i>=5:
    break
  img = cv2.imread(directory_path+"/"+fname)
  img = cv2.resize(img,(800,500))
  undistorted_img = cv2.undistort(img, mtx, dist)
  cv2_imshow(img)
  cv2.waitKey(0)

errors = []
for i in range(len(objpoints)):
    imgpoints2, _ = cv2.projectPoints(objpoints[i], rvecs[i], tvecs[i], mtx, dist)
    error = cv2.norm(imgpoints[i],imgpoints2, cv2.NORM_L2)/len(imgpoints2)
    errors.append(error)

np.save(path+"reprojection-errors", errors)
# Plot the re-projection error as a bar chart
plt.bar(range(len(errors)), errors)
plt.xlabel('Image index')
plt.ylabel('Re-projection error')
plt.show()

# Compute mean and standard deviation of re-projection error
mean_error = np.mean(errors)
std_error = np.std(errors)
print("Mean re-projection error: ", mean_error)
print("Standard deviation of re-projection error: ", std_error)

fig = plt.figure(figsize=(20, 20))
rows = 5
cols = 5

directory_path = '/content/drive/MyDrive/CV_Asgn1/images'
directory_files = os.listdir(directory_path)

for i,fname in enumerate(directory_files):
  img = cv2.imread(directory_path+"/"+fname)
  img = cv2.resize(img,(800,500))
  gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

 
  # find the chessboard corners
  ret, corners = cv2.findChessboardCorners(gray, CHECKERBOARD,None)
  if ret == True:
    corners2 = cv2.cornerSubPix(gray, corners, (11,11), (-1,-1), criteria)

    # project the 3D points to the 2D image plane
    imgpoints2, _ = cv2.projectPoints(objp, rvecs[i], tvecs[i], mtx, dist)

    # draw the detected corners and the re-projected corners onto the image
    img = cv2.drawChessboardCorners(img, CHECKERBOARD, corners2, ret)
    img = cv2.drawChessboardCorners(img, CHECKERBOARD, imgpoints2, True)

    # plot the image with detected corners and re-projected corners
    print("Image "+str(i+1))
    cv2_imshow(img)
    cv2.waitKey(0)
 
cv2.destroyAllWindows()

path= "/content/drive/MyDrive/CV_Asgn1/Q1_Matrices/"

rvecs= np.load(path+"rotation_vectors.npy")
tvecs= np.load(path+"translation_vectors.npy")
imgpoints= np.load(path+"imgpoints.npy")
objp = np.zeros((49, 3), np.float32)
objp[:,:2] = np.mgrid[0:7, 0:7].T.reshape(-1, 2)

dir_path= "/content/drive/MyDrive/CV_Asgn1/images/"
dir_files= os.listdir(dir_path) 

plane_normals=[]
for i,fname in enumerate(dir_files):
  img = cv2.imread(dir_path+fname)
  corners= imgpoints[i]
  # roation matrix from roatation vectors
  R, _ = cv2.Rodrigues(rvecs[i])
  # Compute the extrinsic matrix
  extrinsic = np.hstack((R, tvecs[i]))
  # Compute the 3D corner points in the camera coordinate frame
  points_3d = cv2.convertPointsToHomogeneous(objp)
  points_3d_cam = np.matmul(extrinsic, points_3d.reshape(-1, 4).T).T
  point1 = points_3d_cam[5]
  point2 = points_3d_cam[6]
  point3 = points_3d_cam[7]
  normal = np.cross(point2 - point1, point3 - point1)
  normal /= np.linalg.norm(normal)
  plane_normals.append(normal)

np.save(path+"camer_plane_normals",plane_normals)

"""# Q2"""

!pip install open3d

import open3d as o3d
import numpy as np
import os

path = "/content/drive/MyDrive/CV_Asgn1/Q2/"
lcd_dir = path+"lidar_scans/"

plane_normals=[]
offsets=[]

for fname in os.listdir(lcd_dir):
# Load planar LIDAR points from pcd file
  pcd = o3d.io.read_point_cloud(lcd_dir+fname)
  points = np.asarray(pcd.points)
  A = points - np.mean(points, axis=0)
  u, s, vh = np.linalg.svd(A)
  plane_normals.append(vh[-1, :])
  offsets.append(np.dot(vh[-1,:], np.mean(points, axis=0)))

save_path = path+"matrices/"
np.save(save_path, plane_normals)
np.save(save_path, offsets)

"""## Q2 3)"""

objp = np.zeros((49, 3), np.float32)
objp[:,:2] = np.mgrid[0:7, 0:7].T.reshape(-1, 2)

dir_files = os.listdir(path+"camera_parameters")

camera_normals=[]
camera_offsets=[]

for fname in dir_files:
  cam_norm = open(path+"camera_parameters/"+fname+"/camera_normals.txt").readlines()
  cam_norm = [float(i[:-1]) for i in cam_norm]
  camera_normals.append(cam_norm)
  # extrinsic parameters of camera
  R = open(path+"camera_parameters/"+fname+"/rotation_matrix.txt").readlines()
  R = np.array([list(map(float,x.split())) for x in R])
  T = open(path+"camera_parameters/"+fname+"/translation_vectors.txt").readlines()
  T = np.array([list(map(float,x.split())) for x in T])
  # we take the 3d world coordinate of a checkerboard corner and then find its 
  # coordinate in camera frame reference
  point_3d = np.array([1,0,0])
  point_3d_cam = np.matmul(point_3d,R) + T.squeeze()
  # now we have a point and camera norma with us, so we can get the offset of 
  # the checkerbaord plane using eqn- theta.x - d=0
  d = np.dot(cam_norm,point_3d_cam)
  camera_offsets.append(d)

theta_L= np.array(plane_normals)
alpha_L= np.array(offsets)
theta_C= np.array(camera_normals)
alpha_C= np.array(camera_offsets)

print(theta_C.shape,alpha_L.shape)

# using the procedure given in thesis
t = np.matmul(np.matmul(np.matmul(theta_C.T,theta_C),theta_C.T),alpha_C - alpha_L)
u,s,vt = np.linalg.svd(np.matmul(theta_L.T,theta_C))
R = np.matmul(vt.T,u.T)
# =final Transformation matrix 
Trans_C_L = np.hstack((R,t.reshape(3,1)))
np.save(save_path+"transformation_matrix",Trans_C_L)

"""## Q2 4)"""

# calculate intrinsic matrix
CHECKERBOARD = (8,6)
criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 30, 0.001)
imgpoints = []
objpoints = [] 
objp = np.zeros((CHECKERBOARD[0] * CHECKERBOARD[1], 3), np.float32)
objp[:,:2] = np.mgrid[0:CHECKERBOARD[0], 0:CHECKERBOARD[1]].T.reshape(-1, 2)
img_dir = os.listdir(path+"camera_images")

for fname in img_dir:
  img = cv2.imread(path+"camera_images/"+fname)
  img = cv2.resize(img,(800,500))
  gray = cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)
  ret, corners = cv2.findChessboardCorners(gray, CHECKERBOARD,None)
  if ret == True:
    objpoints.append(objp)
    corners2 = cv2.cornerSubPix(gray, corners, (11,11),(-1,-1), criteria)
    imgpoints.append(corners2)

# mtx is the intrinsic matrix
ret, cam_mtx, dist, rvecs, tvecs = cv2.calibrateCamera(objpoints, imgpoints, gray.shape[::-1], None, None)

imgpoints2=[]
for fname in os.listdir(lcd_dir):
# Load planar LIDAR points from pcd file
  pcd = o3d.io.read_point_cloud(lcd_dir+fname)
  lidar_points = cv2.convertPointsToHomogeneous(np.asarray(pcd.points))
  # converting to camera frame of reference using the transformation
  cam_lidar_points = np.matmul(Trans_C_L, lidar_points.reshape(-1, 4).T).T
  #projecting to image plane using intrinsic matrix
  img_plane_points = np.matmul(cam_mtx,cam_lidar_points.T).T 
  img_plane_points = img_plane_points[:,:-1]/img_plane_points[:,-1][:,np.newaxis]
  imgpoints2.append(img_plane_points)

np.save(save_path+"LIDAR_points_imgPlane",imgpoints2)

"""##Q2 5) """

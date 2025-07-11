import cv2
import numpy as np
from open3d import open3d
import os
import struct

imgfmt = ".jpg"
baseReadPath = "./captures/"
datasets = ["WaterBottle"] # object folder name
CalibAtribs = np.load("./camera_calibration_out/calculated_cams_matrix.npz")
retval=CalibAtribs["retval"]
cameraMatrix1=CalibAtribs["cameraMatrix1"]
distCoeffs1=CalibAtribs["distCoeffs1"]
cameraMatrix2=CalibAtribs["cameraMatrix2"]
distCoeffs2=CalibAtribs["distCoeffs2"]
R=CalibAtribs["R"]
T=CalibAtribs["T"]
E=CalibAtribs["E"]
F=CalibAtribs["F"]
newcameramtx_camera=CalibAtribs["newcameramtx_camera"]
roi_camera=CalibAtribs["roi_camera"]
newcameramtx_proj=CalibAtribs["newcameramtx_proj"]
roi_proj=CalibAtribs["roi_proj"]
invCamMtx=CalibAtribs["invCamMtx"]
invProjMtx=CalibAtribs["invProjMtx"]

projector_resolution =(1920, 1080)

T=T[:,0]
for dataset in datasets:
    for captureFolder in os.listdir(baseReadPath+dataset):
        print(datasets)
        if not os.path.isdir(baseReadPath+dataset+"/"+captureFolder):
            continue
        path = baseReadPath+dataset+"/"+captureFolder + "/"

        img = cv2.imread(path+"w.jpg")
        validV = cv2.imread(path + "out_InvalidImageV.tiff", cv2.IMREAD_GRAYSCALE)
        validH = cv2.imread(path + "out_InvalidImageH.tiff", cv2.IMREAD_GRAYSCALE)
        coordsV = cv2.imread(path + "out_BinImageH.tiff", cv2.IMREAD_ANYDEPTH + cv2.IMREAD_GRAYSCALE)
        coordsH = cv2.imread(path + "out_BinImageV.tiff", cv2.IMREAD_ANYDEPTH + cv2.IMREAD_GRAYSCALE)

        indImg1 = np.indices(coordsH.shape, coordsH.dtype)
        indImg1 = indImg1[:, np.logical_and(validV == 0, validH == 0)]

        colors = img[indImg1[0], indImg1[1]]

        indImg2 = np.vstack((coordsH[indImg1[0], indImg1[1]], coordsV[indImg1[0], indImg1[1]]))
        indImg1[[0, 1]] = indImg1[[1, 0]]
        indImg2[[0, 1]] = indImg2[[1, 0]]
        indImg1 = indImg1.T.astype(np.float64)
        indImg2 = indImg2.T.astype(np.float64)

        LPts = cv2.convertPointsToHomogeneous(cv2.undistortPoints(indImg1[None,], cameraMatrix1, distCoeffs1, R=R))[:,0].T
        RPts = cv2.convertPointsToHomogeneous(cv2.undistortPoints(indImg2[None,], cameraMatrix2, distCoeffs2))[:,0].T


        TLen = np.linalg.norm(T)
        NormedL = LPts/np.linalg.norm(LPts, axis=0)
        alpha = np.arccos(np.dot(-T, NormedL)/TLen)
        degalpha = alpha*180/np.pi
        beta = np.arccos(np.dot(T, RPts)/(TLen*np.linalg.norm(RPts, axis=0)))
        degbeta = beta*180/np.pi
        gamma = np.pi - alpha - beta
        P_len = TLen*np.sin(beta)/np.sin(gamma)
        Pts = NormedL*P_len

        colors[:,[0,2]]=colors[:,[2,0]]

        pcd = open3d.geometry.PointCloud()
        pcd.points = open3d.utility.Vector3dVector(Pts.T)
        pcd.colors = open3d.utility.Vector3dVector(colors.astype(np.float64)/255.0)
        open3d.io.write_point_cloud(baseReadPath+dataset+"/"+"capturedPointCloud_"+captureFolder + ".ply", pcd)

        with open(baseReadPath+dataset+"/"+"capturedPointCloud_"+captureFolder + ".bin", "wb") as fp:
            fp.write(struct.pack("i", len(Pts.T)))
            for pt in Pts.T:
                fp.write(struct.pack("i", 3)+struct.pack("d",pt[0])+struct.pack("d",pt[1])+struct.pack("d",pt[2]))

        downpcd = pcd.voxel_down_sample(voxel_size=0.5)
        # downpcd, ind = open3d.statistical_outlier_removal(downpcd,
        #                                             nb_neighbors=30, std_ratio=3)
        # downpcd = open3d.voxel_down_sample(cl, voxel_size=0.2)

        open3d.io.write_point_cloud(baseReadPath+dataset+"/"+"downsampled_capturedPointCloud_"+captureFolder + ".ply", downpcd)

        with open(baseReadPath+dataset+"/"+"downsampled_capturedPointCloud_"+captureFolder + ".bin", "wb") as fp:
            fp.write(struct.pack("i", len(downpcd.points)))
            for pt in downpcd.points:
                fp.write(struct.pack("i", 3)+struct.pack("d",pt[0])+struct.pack("d",pt[1])+struct.pack("d",pt[2]))


        pts_hold = np.array(downpcd.points)
        colors_hold = np.array(downpcd.colors)
        filterLocs = np.logical_and(
            np.logical_and(pts_hold[:, 2] < 1567537, pts_hold[:, 2] > -8836782),          # z range
            np.logical_and(
                np.logical_and(pts_hold[:, 0] < 3992105, pts_hold[:, 0] > -791900),     # x range
                np.logical_and(pts_hold[:, 1] < 2826662, pts_hold[:, 1] > -221705)      # y range
            )
        )
        ###############################################

        #print(f"pts_hold x range: {np.min(pts_hold[:, 0])} to {np.max(pts_hold[:, 0])}")
        #print(f"pts_hold y range: {np.min(pts_hold[:, 1])} to {np.max(pts_hold[:, 1])}")
        #print(f"pts_hold z range: {np.min(pts_hold[:, 2])} to {np.max(pts_hold[:, 2])}")
        #print(f"Total points before filtering: {pts_hold.shape[0]}")
        #print("")

        #print("Before filtering:")
        #print(" - Total points:", len(pts_hold))

        # Show filtering mask stats
        #print(" - filterLocs shape:", filterLocs.shape)
        #print(" - Num kept:", np.sum(filterLocs))
        #print(" - Num removed:", len(filterLocs) - np.sum(filterLocs))

        #print("pts_hold x range:", pts_hold[:,0].min(), pts_hold[:,0].max())
        #print("pts_hold y range:", pts_hold[:,1].min(), pts_hold[:,1].max())
        #print("pts_hold z range:", pts_hold[:,2].min(), pts_hold[:,2].max())

        ##################################################
        pts_hold = pts_hold[filterLocs]
        colors_hold = colors_hold[filterLocs]
        pcd = open3d.geometry.PointCloud()
        pcd.points = open3d.utility.Vector3dVector(pts_hold)
        pcd.colors = open3d.utility.Vector3dVector(colors_hold)
        open3d.io.write_point_cloud(baseReadPath + dataset + "/" + "filtered__capturedPointCloud__" + captureFolder + ".ply", pcd)

        with open(baseReadPath + dataset + "/" + "filtered__capturedPointCloud__" + captureFolder + ".bin", "wb") as fp:
            fp.write(struct.pack("i", len(pcd.points)))
            for pt in pcd.points:
                fp.write(
                    struct.pack("i", 3) + struct.pack("d", pt[0]) + struct.pack("d", pt[1]) + struct.pack("d", pt[2]))

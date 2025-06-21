from cv2 import aruco
 
#A4_shape = 2480, 3508
#A4_shape_1cm_margin = 2280, 3308
#outshape = 2380*4, 3308*4
#8.5_shape = 2550, 3300
#8.5_shape_1cm_margin = 2350, 3100
#outshape = 2380*4, 3308*4

dpmm = 40 # Dots per millimeter used for scaling
A4_shape = 216, 279 # A4 paper size in mm
A4_shape_margin = A4_shape[0]-10, A4_shape[1] - 20  
outshape = A4_shape[0]*dpmm, A4_shape[1]*dpmm
desired_block_size_mm = 30
desired_aruco_size_mm = 21
desired_gap_size_mm = 5 #gap between markers of Aruco board
 
blocksx = A4_shape[0]//desired_block_size_mm # Horizontal number of blocks
blocksy = A4_shape[1]//desired_block_size_mm # Vertical number of blocks
 
arucoDict = aruco.getPredefinedDictionary(aruco.DICT_4X4_250)

charucoBoard = aruco.CharucoBoard(
                                         (blocksx, blocksy), # Number of markers in X,Y coordinate system
                                         desired_block_size_mm, # Size of a square in mm
                                         desired_aruco_size_mm, #size of Aruco marker
                                         arucoDict) 
 
 
blocksx2 = (A4_shape[0]+desired_gap_size_mm)//(desired_block_size_mm+desired_gap_size_mm)
blocksy2 = (A4_shape[1]+desired_gap_size_mm)//(desired_block_size_mm+desired_gap_size_mm)
 
arucoBoard = aruco.GridBoard(
                              (blocksx2, blocksy2), # Number of markers in (X, Y)
                              desired_block_size_mm, #Marker size
                              desired_gap_size_mm,  #marker gap size
                              arucoDict)

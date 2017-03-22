"""Makes the training labels - pulls in re-drawn lane lines
in perspective transformed images, is thresholded on red
(since the lines were re-drawn over in red), uses sliding window
detection to calculate the fit coefficients for both lines,
and save the labels to a pickle file for later.
"""

import numpy as np
import os
import cv2
import matplotlib.image as mpimg
import matplotlib.pyplot as plt
import glob
import pickle
import re

def natural_key(string_):
    """See http://www.codinghorror.com/blog/archives/001018.html"""
    return [int(s) if s.isdigit() else s for s in re.split(r'(\d+)', string_)]

def load_drawn_images():
    """Load re-drawn lane image locations"""
    drawn_image_locs = glob.glob('draw/*.jpg')
    sort_drawn_image_locs = sorted(drawn_image_locs, key=natural_key)
    counter = 0
    for fname in sort_drawn_image_locs:
        img = mpimg.imread(fname)
        drawn_images.append(img)     

def pipeline(img, R_thresh = (230, 255)):
    """Threshold the re-drawn images for high red threshold"""
    img = np.copy(img)
    R = img[:,:,0]
 
    R_binary = np.zeros_like(R)
    R_binary[(R >= R_thresh[0]) & (R <= R_thresh[1])] = 1

    combined_binary = np.zeros_like(R_binary)
    combined_binary[(R_binary == 1)] = 1
    return combined_binary

# Make a list to hold the re-drawn lane images
drawn_images = []

# Load in the re-drawn lane images, appending to drawn_images
load_drawn_images()

# Make a list to hold the binary thresholded images
binary_bird = []

# Iterate through each image to threshold it and append to binary_bird
for image in drawn_images:
    binary_image = pipeline(image)
    binary_bird.append(binary_image)

# Make a list to hold the 'labels' - six coefficients, two for each line
lane_labels = []

def lane_detection(image_list):
    """Iterates through each binary thresholded image. Uses sliding
    windows to detect lane points, and fits lines to these points.
    The polynomial coefficients of this line are then appended to
    the lane_labels list as those will be the training labels.
    The below code is a modified version of my computer vision-based
    Advanced Lane Lines project.
    """
    for binary_warped in image_list:
        # Assuming you have created a warped binary image called "binary_warped"
        # Take a histogram of the bottom half of the image
        histogram = np.sum(binary_warped[binary_warped.shape[0]/2:,:], axis=0)
        # Create an output image to draw on and  visualize the result
        out_img = np.dstack((binary_warped, binary_warped, binary_warped))*255
        # Find the peak of the left and right halves of the histogram
        # These will be the starting point for the left and right lines
        midpoint = np.int(histogram.shape[0]/2)
        leftx_base = np.argmax(histogram[:midpoint])
        rightx_base = np.argmax(histogram[midpoint:]) + midpoint

        # Choose the number of sliding windows
        nwindows = 9
        # Set height of windows
        window_height = np.int(binary_warped.shape[0]/nwindows)
        # Identify the x and y positions of all nonzero pixels in the image
        nonzero = binary_warped.nonzero()
        nonzeroy = np.array(nonzero[0])
        nonzerox = np.array(nonzero[1])
        # Current positions to be updated for each window
        leftx_current = leftx_base
        rightx_current = rightx_base
        # Set the width of the windows +/- margin
        margin = 100
        # Set minimum number of pixels found to recenter window
        minpix = 50
        # Create empty lists to receive left and right lane pixel indices
        left_lane_inds = []
        right_lane_inds = []

        # Step through the windows one by one
        for window in range(nwindows):
            # Identify window boundaries in x and y (and right and left)
            win_y_low = binary_warped.shape[0] - (window+1)*window_height
            win_y_high = binary_warped.shape[0] - window*window_height
            win_xleft_low = leftx_current - margin
            win_xleft_high = leftx_current + margin
            win_xright_low = rightx_current - margin
            win_xright_high = rightx_current + margin
            # Draw the windows on the visualization image
            cv2.rectangle(out_img,(win_xleft_low,win_y_low),(win_xleft_high,win_y_high),(0,255,0), 2) 
            cv2.rectangle(out_img,(win_xright_low,win_y_low),(win_xright_high,win_y_high),(0,255,0), 2) 
            # Identify the nonzero pixels in x and y within the window
            good_left_inds = ((nonzeroy >= win_y_low) & (nonzeroy < win_y_high) & (nonzerox >= win_xleft_low) & (nonzerox < win_xleft_high)).nonzero()[0]
            good_right_inds = ((nonzeroy >= win_y_low) & (nonzeroy < win_y_high) & (nonzerox >= win_xright_low) & (nonzerox < win_xright_high)).nonzero()[0]
            # Append these indices to the lists
            left_lane_inds.append(good_left_inds)
            right_lane_inds.append(good_right_inds)
            # If you found > minpix pixels, recenter next window on their mean position
            if len(good_left_inds) > minpix:
                leftx_current = np.int(np.mean(nonzerox[good_left_inds]))
            if len(good_right_inds) > minpix:        
                rightx_current = np.int(np.mean(nonzerox[good_right_inds]))

        # Concatenate the arrays of indices
        left_lane_inds = np.concatenate(left_lane_inds)
        right_lane_inds = np.concatenate(right_lane_inds)

        # Extract left and right line pixel positions
        leftx = nonzerox[left_lane_inds]
        lefty = nonzeroy[left_lane_inds] 
        rightx = nonzerox[right_lane_inds]
        righty = nonzeroy[right_lane_inds] 

        # Fit a second order polynomial to each
        left_fit = np.polyfit(lefty, leftx, 2)
        right_fit = np.polyfit(righty, rightx, 2)
        
        # Append to the labels list
        lane_labels.append([np.append(left_fit, right_fit)])

# Run through all the images
lane_detection(binary_bird)

# Save the final list to a pickle file for later
pickle.dump(lane_labels,open('lane_labels.p', "wb" ))
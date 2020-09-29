#!/usr/bin/env python
# coding: utf-8

## python raw2reflectance.py input_dir output_dir

# Radiometric Calibration with Sun Irradiance Sensor (= DLS Sensor)
# Raw Image (.TIF) --> Reflectance Image (.TIF, Scale: 0-2**16)
# Reflectance Image / 2**16 --> 0-1 value

import os, glob
import numpy as np
import tifffile
import micasense.capture as capture
import micasense.dls as dls
import micasense.metadata as metadata
import time
import sys
import exiftool
import json

input_dir = sys.argv[1]
output_dir = sys.argv[2]

start = time.time()

initial_path = os.getcwd()

# Raw Image (.TIF) should be in path "raw_images"
raw_image_list = glob.glob(os.path.join(input_dir,'*.TIF'))
#image_names = sorted(glob.glob(os.path.join(os.getcwd()+'/raw_images/100MEDIA_DJI_0192.TIF')))

print("Start Radiometric Calibration")        
for i in range(len(raw_image_list)):

    raw_image = raw_image_list[i]
    print("Processing %s [%d/%d] %.2f percent done." % (os.path.basename(raw_image), i+1, len(raw_image_list), float(i+1)/float(len(raw_image_list)) * 100))

    cap = capture.Capture.from_filelist([raw_image])

    # Define DLS sensor orientation vector relative to dls pose frame
    dls_orientation_vector = np.array([0,0,-1])
    # compute sun orientation and sun-sensor angles
    (
    sun_vector_ned,    # Solar vector in North-East-Down coordinates
    sensor_vector_ned, # DLS vector in North-East-Down coordinates
    sun_sensor_angle,  # Angle between DLS vector and sun vector
    solar_elevation,   # Elevation of the sun above the horizon
    solar_azimuth,     # Azimuth (heading) of the sun
    ) = dls.compute_sun_angle(cap.location(),
                      cap.dls_pose(),
                      cap.utc_time(),
                      dls_orientation_vector)

    # Get Spectral Irradiance (= Sun Sensor Irradiance) for each image from its metadata
    spectral_irradiances=[]

    meta = metadata.Metadata(raw_image, exiftoolPath=None)
    spectral_irradiances.append(meta.get_item('XMP:Irradiance'))

    # With Solar elements & Spectral Irradiance
    # Now we can correct the raw sun sensor irradiance value (DLS)
    # and compute the irradiance on level ground

    dls_irradiances = []

    fresnel_correction = dls.fresnel(sun_sensor_angle)
    dir_dif_ratio = 6.0  # Default value from MicaSense
    percent_diffuse = 1.0/dir_dif_ratio
    sensor_irradiance = spectral_irradiances/fresnel_correction
    untilted_direct_irr = sensor_irradiance / (percent_diffuse + np.cos(sun_sensor_angle))

    # compute irradiance on the ground (= DLS Irradiance) using the solar altitude angle
    dls_irr = untilted_direct_irr * (percent_diffuse + np.sin(solar_elevation))
    dls_irradiances.append(dls_irr)

    # Produce Reflectance Images
    reflectance_image = cap.compute_reflectance(dls_irradiances)
    reflectance_image = np.array(reflectance_image)[0,:,:]

    # Reflectance Images (Float64 --> Int16)
    reflectance_image = np.round(reflectance_image,5)
    reflectance_image = np.round(reflectance_image*2**16)
    reflectance_image = np.uint16(reflectance_image)

    # Change current path to save Reflectance Images
    if not os.path.isdir(output_dir):
        os.mkdir(output_dir)
        os.chdir(os.path.join(os.getcwd(),output_dir))
    else: os.chdir(os.path.join(os.getcwd(),output_dir))

    # Save Reflectance Images (.TIF), whose name is same as the Raw Images (.TIF), in the path "reflectance_images"
    # Insert Metadata by "description = metadata_json"
    filename=os.path.splitext(os.path.basename(raw_image))[0]
    tifffile.imsave('%s.TIF'%filename, reflectance_image)

print("%d reflectance images are created in %s" % (len(raw_image_list),output_dir))

os.chdir(initial_path)

raw_image_list = glob.glob(os.path.join(input_dir,'*.TIF'))
ref_image_list = glob.glob(os.path.join(output_dir,'*.TIF'))

print("Strat Copying Metadata")  
for i in range(len(raw_image_list)):
    
    print("Processing %s [%d/%d] %.2f percent done." % (os.path.basename(raw_image), i+1, len(raw_image_list), float(i+1)/float(len(raw_image_list)) * 100))
    
    raw_image = raw_image_list[i]
    ref_image = ref_image_list[i]
    if os.path.basename(raw_image)!=os.path.basename(ref_image):
        print("warning. metadata does not match")
    os.system('exiftool -TagsFromFile {raw} -all:all -xmp -overwrite_original {ref}'.format(raw=raw_image,ref=ref_image))

print("it takes %.2f seconds" %(time.time()-start))


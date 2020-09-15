import xml.etree.ElementTree as ET
import matplotlib.pyplot as plt
from PIL import Image
import numpy as np
import cv2
import os
import argparse
from utils import *
from config import config as cfg
import re

# Process the XML file with incorrect hierarchy.
def process_incorrect_xml(label_path, fpath, file):
    # extract a single channel from the label.
    label_image = cv2.imread(label_path)[:,:,0] 

    # create two dictionaries - one for the explants and other for the tissue parts.
    explants_map = dict()
    tissues_map = dict()

    saveFlag = True

    # Parse the file into a tree.
    file = os.path.join(fpath, file)
    tree = ET.parse(file)
    # fetch the root node.
    root = tree.getroot()

    for c in root:
        if c.tag == "hierarchyStack":
            for i, child in enumerate(c, 1):
                tissue_explant = child.find('name').text
                explant_id = int(re.sub("[a-zA-Z]", '', tissue_explant))

                if explant_id not in explants_map:
                    explants_map[explant_id] = []
                
                classes = child.find('classes')    
                if classes:
                    for j, child2 in enumerate(classes):

                        # obtain the plant tissue name and its corresponding id.
                        tname = child2.find('name').text.lower()
                        uid = int(child2.find('uid').text)

                        if tname not in tissues_map:
                            tissues_map[tname] = []
                        
                        # update the dictionaries
                        tissues_map[tname].append(uid)
                        explants_map[explant_id].append(uid)

                    # create a plant tissues image.
                    tissues_image = np.zeros(label_image.shape)
                    for tname in tissues_map:
                        for uid in tissues_map[tname]:
                            tissues_image[label_image==uid] = cfg.assign_labels[tname]
                    
                    # explant image
                    explant_image = np.zeros(label_image.shape)
                    for explant in explants_map:
                        for uid in explants_map[explant]:
                            explant_image[label_image==uid] = explant
                    
                else:
                    saveFlag = False
                    print("Hierarchy stack is empty.")
                    return saveFlag, _, _
    return saveFlag, tissues_image, explant_image


# Function to process the labels of an image
def process_label(label_path, fpath, file):
    # extract a single channel from the label.
    label_image = cv2.imread(label_path)[:,:,0] 

    # create two dictionaries - one for the explants and other for the tissue parts.
    explants_map = dict()
    tissues_map = dict()

    saveFlag = True

    # Parse the file into a tree.
    file = os.path.join(fpath, file)
    tree = ET.parse(file)
    # fetch the root node.
    root = tree.getroot()

    # fetch the hierarchy stack (Necrotic/Callus/Stem/Shoot)
    for c in root:
        if c.tag == "hierarchyStack":
            for i, child in enumerate(c, 1):
                explants_map[i] = []
                classes = child.find('classes')
                    
                if classes:
                    for j, child2 in enumerate(classes):

                        # obtain the plant tissue name and its corresponding id.
                        tname = child2.find('name').text.lower()
                        uid = int(child2.find('uid').text)

                        if tname not in tissues_map:
                            tissues_map[tname] = []
                        
                        # update the dictionaries
                        tissues_map[tname].append(uid)
                        explants_map[i].append(uid)

                    # create a plant tissues image.
                    tissues_image = np.zeros(label_image.shape)
                    for tname in tissues_map:
                        for uid in tissues_map[tname]:
                            tissues_image[label_image==uid] = cfg.assign_labels[tname]
                    
                    # explant image
                    explant_image = np.zeros(label_image.shape)
                    for explant in explants_map:
                        for uid in explants_map[explant]:
                            explant_image[label_image==uid] = explant
                    
                else:
                    saveFlag = False
                    print("Hierarchy stack is empty.")
                    return saveFlag, _, _
    return saveFlag, tissues_image, explant_image
    

# Function to parse the images.
def parse_files(file_path, save_color):
    # create directories
    create_dir('labels')
    deeplab_path = os.path.join('labels', "deeplab")
    ann_path = os.path.join('labels', "annotation")
    create_dir(deeplab_path)
    create_dir(ann_path)

    tissues_deeplab_path = os.path.join(deeplab_path, "tissues")
    explant_deeplab_path = os.path.join(deeplab_path, "explants")
    create_dir(tissues_deeplab_path)
    create_dir(explant_deeplab_path)

    tissues_ann_path = os.path.join(ann_path, "tissues")
    explant_ann_path = os.path.join(ann_path, "explants")
    create_dir(tissues_ann_path)
    create_dir(explant_ann_path)

    # color palette
    palette = color_map()
    # palette = palette.reshape(-1, 1)

    # list all the image files from the path.
    files = os.listdir(file_path)

    for file in files:
        if file.endswith('.xml'):
            # label image file
            label_path = os.path.join(file_path, '.'.join(file.split('.')[:-1])+"_inst_class_gray.png")

            if not os.path.exists(label_path):
                gray_inst = '.'.join(file.split('.')[:-1])+"_inst_class_gray.png"
                print("Missing label file: ", gray_inst)
                continue

            saveFlag, tissues_image, explant_image = process_label(label_path, file_path, file)

            if saveFlag:
                if len(np.unique(explant_image)) > 13:
                    saveFlag, tissues_image, explant_image = process_incorrect_xml(label_path, file_path, file)
                    if not saveFlag:
                        print("Incorrect XML file {} was not processed.".format(file))
                        continue
                    print("Incorrect XML file {} was processed by using alternate hierarchy configuration.".format(file))

                # write label and tissues image.
                tpath = os.path.join(tissues_deeplab_path, '.'.join(file.split('.')[:-1])+".png")
                labpath = os.path.join(explant_deeplab_path, '.'.join(file.split('.')[:-1])+".png")

                if save_color:
                    tpath_ann = os.path.join(tissues_ann_path, '.'.join(file.split('.')[:-1])+".png")
                    labpath_ann = os.path.join(explant_ann_path, '.'.join(file.split('.')[:-1])+".png")
                
                # save the images.
                # Deeplab tissue image.
                save_image(tpath, tissues_image)
                save_image(labpath, explant_image)

                if save_color:
                    # Add palette and save colored tissue/explant image.
                    save_color_image(tpath_ann, tissues_image, palette)
                    save_color_image(labpath_ann, explant_image, palette)



if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Read labels')
    parser.add_argument("-fp", '--file_path', required=True, help='Path to the folders')
    parser.add_argument("-save_color", action='store_false', help="Save colored labels.")
    args = parser.parse_args()

    # parse the files.
    parse_files(args.file_path, args.save_color)

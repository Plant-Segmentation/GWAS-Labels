import xml.etree.ElementTree as ET
import matplotlib.pyplot as plt
from PIL import Image
import numpy as np
import cv2
import os
import argparse
import re
from utils import *
from config import config as cfg


# Function to process the labels of an image
def process_label(label_path, fpath, file):
    # extract a single channel from the label.
    label_image = cv2.imread(label_path)[:,:,0] 

    # create two dictionaries - one for the explants and other for the tissue parts.
    explants_map = dict()
    tissues_map = dict()
    
    # Parse the file into a tree.
    file = os.path.join(fpath, file)
    tree = ET.parse(file)
    
    # fetch the root node.
    root = tree.getroot()

    saveFlag = True
    # fetch the hierarchy stack (Necrotic/Callus/Stem/Shoot)
    for c in root:
        if c.tag == "hierarchyStack":   # check the Hierarchy Stack.
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


def parse_files(file_path, file_list, save_color):
    # create directories
    deeplab_path = os.path.join(file_path, "deeplab")
    ann_path = os.path.join(file_path, "annotation")
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

    # list all the image files from the txt file.
    files = open(file_list).readlines()

    for file in files:
        file = file.strip()
        if file.endswith('.xml'):
            # label image file
            label_path = os.path.join(file_path, '.'.join(file.split('.')[:-1])+"_inst_class_gray.png")

            if not os.path.exists(label_path):
                gray_inst = '.'.join(file.split('.')[:-1])+"_inst_class_gray.png"
                print("Missing label file: ", gray_inst)
                continue

            # Process the label file.
            saveFlag, tissues_image, explant_image = process_label(label_path, file_path, file)

            if not saveFlag:
                print("Could not process file: ", file)
                continue
            
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

    if cfg.incorrect_xml:
        if not os.path.exists(cfg.incorrect_xml):
            raise Exception("Text file containing list of Incorrect XML files not found.")

    parse_files(args.file_path, cfg.incorrect_xml, args.save_color)


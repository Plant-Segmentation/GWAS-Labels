from PIL import Image
import numpy as np
import os

# Function to create color palette
# PASCAL VOC color palette - https://gist.github.com/wllhf/a4533e0adebe57e3ed06d4b50c8419ae
def color_map(N=256, normalized=False):
    def bitget(byteval, idx):
        return ((byteval & (1 << idx)) != 0)

    dtype = 'float32' if normalized else 'uint8'
    cmap = np.zeros((N, 3), dtype=dtype)
    for i in range(N):
        r = g = b = 0
        c = i
        for j in range(8):
            r = r | (bitget(c, 0) << 7-j)
            g = g | (bitget(c, 1) << 7-j)
            b = b | (bitget(c, 2) << 7-j)
            c = c >> 3

        cmap[i] = np.array([r, g, b])

    cmap = cmap/255 if normalized else cmap
    return cmap


# Function to create a directory.
def create_dir(dir_path):
    if not os.path.exists(dir_path):
        os.mkdir(dir_path)


# Function to save the image.
def save_image(fname, img_arr):
    pil_image = Image.fromarray(img_arr.astype(dtype=np.uint8))
    pil_image.save(fname, 'PNG')

# Function to save the image.
def save_color_image(fname, img_arr, palette):
    pil_image = Image.fromarray(img_arr.astype(dtype=np.uint8))
    pil_image.putpalette(palette)
    pil_image.save(fname, 'PNG')
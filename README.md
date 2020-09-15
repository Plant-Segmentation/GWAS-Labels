# GWAS-Labels
This repository contains the scripts to process the GWAS Annotation Labels.

## Setup environment
You can either install the dependencies for running the scripts using the uploaded yml or follow the below instructions to install them manually.

### Create environment using yaml
```
conda env create --file GWAS.yml
```

### Manual installation
1. Create a conda environment.
```
conda create -n GWAS python=3.6
```

2. Activate conda environment.
```
conda activate GWAS
```

3. Install packages:
```
conda install -c conda-forge opencv
conda install -c conda-forge easydict
conda install scikit-image
```

## Create labels
1. Place the XML files and gray scale annotation files inside the same folder in the main directory.

2. Run the script using the command -
```
python process_labels.py -fp folder_path
```

If you wish to exclude the colored labels. Use the command -
```
python process_labels.py -fp folder_path -save_color
```

The result folder 'labels/' will be created inside the main directory.

- Label
  - Deeplab (Deeplab style annotations)
    - Tissues
    - Explants
  - Annotation  (Colored annotaions)
    - Tissues
    - Explants

from easydict import EasyDict as edict

config = edict()

# dictionary of labels
config.assign_labels = {'background': 0, 'stem': 1, 'callus': 2, 'shoot': 3, 'root': 4, 'contam': 5, 'contamination': 5, 'necrotic tissue': 5, 'necrotic issue': 5}

config.incorrect_xml = 'incorrect_xml.txt'
# mtg-image-recognition

This small project is just for fun and playing with image recognition of MTG cards.

# database_builder

The database_builder.py downloads images and card metadata from srcyfall. The images are saved to ```data/mtg_<3_digit_setcode>``` and the metadata usable for labeling as a json.

Currently only standard expansions and core sets after Mirroding and including Kaldheim are downloaded. This is done to minimize duplicate cards and only use modern border to have a more homogenous data set. Code must be adjusted to modify this behavior. 


# config

The config.json is used to store some config data.

# Actual image recognition

Currently the main functionality is still to be done.
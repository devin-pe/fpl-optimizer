from clean import load
import config
import numpy as np
import preprocess

def populate():
    szn = config.end_season
    gw_df = load('gw', dir='processed_data', szn=szn, cols=None)
    player_df = load('play', dir='processed_data', szn=szn, cols=None)

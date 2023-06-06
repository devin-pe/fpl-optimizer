import config
from preprocess import *

szn = config.end_season
gw_df = load('gw', dir='processed_data', szn=szn, cols=None)
player_df = load('play', dir='processed_data', szn=szn, cols=None)

players = init_team(2, gw_df, player_df)
for plyr in players:
    print('Past: ', plyr.get_past_pts())
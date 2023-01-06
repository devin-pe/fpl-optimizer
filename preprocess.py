import pandas as pd
import config as cfg
from os import path

def load(category, szn):
    if category == 'gw':
        fpath = path.join('original_data', f'merged_gw_{szn}_{szn+1}.csv')
    elif category == 'player':
        fpath = path.join('original_data', f'players_{szn}_{szn+1}.csv')
    else:
        fpath = path.join('data', f'blended_gw_{szn}_{szn+1}.csv')
    df = pd.read_csv(fpath, encoding='latin-1')
    return df

def add_posn():
    """Adds the position of a player to a line in the merged gw files.
    A naive approach is to do it for one week and copy it for all remaining gameweeks.
    The problem is that players can be transfered in and out of the league.
    Hence, we locate all players by id for each gw"""
    for szn in range(cfg.start_season, cfg.end_season+1):
        print(f'Processing season {szn}-{szn+1}')
        player_df = load('player', szn)
        merged_gw_df = load('gw', szn)
        pos_coln = []
        for gw in range(1, cfg.n_gameweeks+1):
            gw_stats = merged_gw_df.loc[merged_gw_df['GW'] == gw]
            for i in gw_stats.index:
                id = gw_stats.loc[i, 'element']                                         # locate player with id at index i in gw_stats
                player = player_df.loc[player_df['id'] == id].iloc[0]                   # match the id in the gw file to the id in the player file 
                pos_coln.append(player.loc['element_type'])                             # add the position of that player to an array
        merged_gw_df['pos'] = pos_coln                                                  # add the filled position column to df
        fpath = path.join('temp_data', f'merged_pos_{szn}_{szn+1}.csv')
        merged_gw_df.to_csv(fpath)                                                      # save df as .csv
        print(f'Done with season {szn}-{szn+1}')

def blend_data():
    for szn in range(cfg.start_season, cfg.end_season+1):
        gw_df = load('gw', szn)
        player_df = load('player', szn)


def main():
    add_posn()

main()



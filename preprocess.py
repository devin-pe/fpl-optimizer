import pandas as pd
import config as cfg
from os import path
import re

# <--- Not used --->
'''
def check_names():
    """
    Match player names in both datasets (one has been double encoded in UTF-8).
    Then, change the player dataset."""
    for szn in range(cfg.start_season, cfg.end_season+1):
        gw_df = load('gw', szn)
        player_df = load('player', szn)
        print('----------------------')
        print(f'Starting season {szn}')
        print('----------------------')
        count = 0
        for i in range(len(player_df['first_name'])):
            fname_list = player_df['first_name'].iloc[i].split()
            sname = player_df['second_name'].iloc[i]
            name = fname_list[0]
            for mname in fname_list[1:]:
                name += ' ' + mname
            name += '_' + sname
            encoded_name = name.encode('raw_unicode_escape').decode('utf-8')
            encoded_gw_names = [n for n in gw_df['name']]
            if encoded_name not in encoded_gw_names:
                print(encoded_name)
                count += 1
        print(count)

def find_veterans():
    """Find players which played in all seasons"""
    prev_names = []
    for szn in range(cfg.start_season, cfg.end_season+1):  
        player_df = load('player', szn)
        curr_names = []
        for i in range(len(player_df['first_name'])):               # Add first and second name(s) to the list
            fnames = player_df['first_name'].iloc[i]
            sname = player_df['second_name'].iloc[i]
            curr_names.append((fnames, sname))
        if not prev_names:                                          # Set previous names for the first time
            prev_names = curr_names[:]
        else:
            prev_names = [n for n in prev_names if n in curr_names] # Add names to the new version of prev_names 
                                                                    # if they are in prev_names and are in curr_names
    return prev_names                                               # return players which played in all seasons


def find_consistent_field():
    """Find fields for which values are consistent across seasons for a given player"""
    # There are 2 potential fields which could be the same across seasons: code and photo
    codes = []
    photos = []
    vets = find_veterans()
    for szn in range(cfg.start_season, cfg.end_season+1):  
        player_df = load('player', szn)
        for i in range(len(vets)):
            player_subset = player_df.loc[player_df['first_name'] == vets[i][0]]    # find players by filtering by 1st name
            player = player_subset.loc[player_df['second_name'] == vets[i][1]]      # find the desired player by filtering by 2nd name
            if player['code'].iloc[0] not in codes:
                codes.append(player['code'].iloc[0])                                # Add unique code to codes
            if player['photo'].iloc[0] not in photos:
                photos.append(player['photo'].iloc[0])                              # Add unique photos to photos
    print(len(codes), len(photos), len(vets))                                       # These numbers should hopefully be the same, but are not
'''
#<--- Not used --->

def load(category, szn, cols=None):
    """Loads the the different categories of files containaing the data.
    'gw' for merged gameweek, 'player' for summary player data"""
    if category == 'gw':
        fpath = path.join('data', f'merged_gw_{szn}_{szn+1}.csv')
    elif category == 'player':
        fpath = path.join('data', f'players_{szn}_{szn+1}.csv')
    else:
        raise Exception('No files of the given category')
    df = pd.read_csv(fpath, encoding='latin-1', usecols=cols)
    return df

def remove_postfix(names):
    """Remove the numbers added to the end of names in the gw files in seasons 18-20"""
    new_names = []
    for name in names:
        for i, c in enumerate(name[::-1]):
            if c == '_':                                    # use i when underscore is found
                new_names.append(name[:len(name)-(i+1)])    # slice name to take chars before underscore
                break
    return new_names

def get_pos(player_df, gw_df):
    """Adds the position of a player to a line in the merged gw files.
    A naive approach is to do it for one week and copy it for all remaining gameweeks.
    The problem is that players can be transfered in and out of the league.
    Hence, we locate all players by id for each gw"""
    pos = []
    for gw in range(1, max(gw_df['GW'])+1):
        gw_stats = gw_df.loc[gw_df['GW'] == gw]
        for i in gw_stats.index:
            id = gw_stats.loc[i, 'element']                                         # locate player with id at index i in gw_stats
            player = player_df.loc[player_df['id'] == id].iloc[0]                   # match the id in the gw file to the id in the player file 
            pos.append(player.loc['element_type'])                                  # add the position of that player to an array
    return pos

def get_fullname(name_df):
    """
    Get fullnames by concatenating names from player file into a list"""
    fullnames = []
    for i in range(len(name_df['first_name'])):
        fname_list = name_df['first_name'].iloc[i].split()                          # split (multiple) first names into list
        sname = name_df['second_name'].iloc[i]                                      # get the second name
        name = fname_list[0]                                                        # init list with first name
        for mname in fname_list[1:]:                                                # add all middle names
            name += ' ' + mname
        name += '_' + sname                                                         # separate first names from last name using underscore
        encoded_name = name.encode('raw_unicode_escape').decode('utf-8')            # decode because names are double encoded in dataset
        fullnames.append(encoded_name)
    return fullnames

def assign_id():
    """Assigns unique field identifiers to player 0 thru n-1 across all seasons.
    idmap = {id: fullname}, w ID formed using fullname"""
    id = 0
    idmap = {}
    for szn in range(cfg.start_season, cfg.end_season+1):
        name_df = load('player', szn, cols=['first_name', 'second_name'])         
        fullnames = get_fullname(name_df)                                   # get all the full names for that season
        for player in fullnames:                               
            if player not in set(idmap):                                    # if the player has not been given an ID yet
                idmap[player] = id                                          # assign id to full name   
                id += 1
    return idmap                                            

def order_id_for_gw(idmap, names):
    """Uses id map generated from the player files and orders them for insertion in gw files.
    Full names in map are matched to each line in the gw files"""
    ids = []
    for player in names:
        if player in idmap:                     # check if player has an id
            ids.append(idmap[player])           # add id to list
        else:                                   # if player has no id, throw error
            print(player)
    return ids
    
def save(gw_df, szn):
    """Saves the preprocessed game week dataframe to new location"""
    fpath = path.join('processed_data', f'gw_{szn}_{szn+1}.csv')                        # specify file location
    gw_df.to_csv(fpath, index=False)                                                    # save df as .csv

def main():
    idmap = assign_id()
    for szn in range(cfg.start_season, cfg.end_season+1):  
        print('----------------------')
        print(f'Starting season {szn}')
        print('----------------------')
        gw_df = load('gw', szn, cols=['name', 'total_points', 'value', 'GW'])           # current model only uses 4 fields
        player_df = load('player', szn) 
        names = gw_df['name'].tolist()                                                  # make df into list
        if szn == 18 or szn == 19:                                                      # if gw names have undesired postfix
            names = remove_postfix(names)                                                       # remove them
        ids = order_id_for_gw(idmap, names)                                             # get ids 
        gw_df['id'] = ids                                                               # add them to the dataframe
        #pos = get_pos(player_df, gw_df)                                                # get positions for each row
        #gw_df['pos'] = pos                                                             # add them to the dataframe
        save(gw_df, szn)                                                                       
        print(f'Done with season {szn}-{szn+1}') 

if __name__ == '__main__':
    main()



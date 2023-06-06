import config as cfg
from os import path
import pandas as pd

def load(category, dir=None, szn=None, cols=None):
    """Loads the the different categories of files containaing the data.
    'gw' for merged gameweek, 'player' for summary player data.
    Files are assummed to be stored in """
    # Reading raw data for EA
    if dir == 'data':
        if category == 'gw':
            fpath = path.join(dir, f'merged_gw_{szn}_{szn+1}.csv')
        elif category == 'play':
            fpath = path.join(dir, f'players_{szn}_{szn+1}.csv')
        elif category == 'teams':
            fpath = path.join(dir, f'master_team_list.csv')
        else:
            raise Exception('No files to load from the dir in the given category')
    
    # Reading processed data for EA
    elif dir == 'processed_data':
        if category == 'gw':
            fpath = path.join(dir, f'{category}_{szn}_{szn+1}.csv')                       
        elif category == 'play':
            fpath = path.join(dir, f'{category}_{szn}_{szn+1}.csv')                      
        elif category == 'teams':
            fpath = path.join(dir, f'{category}.csv')
        else:
            raise Exception('No files to load from the dir in the given category')
    df = pd.read_csv(fpath, encoding='latin-1', usecols=cols)
    return df

def save(category, df, szn=None):
    """Saves the preprocessed dataframe to new location"""
    dir = 'processed_data'
    if category == 'gw':
        fpath = path.join(dir, f'{category}_{szn}_{szn+1}.csv')                       
    elif category == 'play':
        fpath = path.join(dir, f'{category}_{szn}_{szn+1}.csv')                      
    elif category == 'teams':
        fpath = path.join(dir, f'{category}.csv')
    else:
        raise Exception('No files to save of the given category')
    df.to_csv(fpath, index=False)                                      

def remove_postfix(names):
    """Remove the numbers added to the end of names in the gw files in seasons 18-19 and 19-20"""
    new_names = []
    for name in names:
        for i, c in enumerate(name[::-1]):
            if c == '_':                                    # use i when underscore is found
                new_names.append(name[:len(name)-(i+1)])    # slice name to take chars before underscore
                break
    return new_names

def rm_underscores(names):
    return [name.replace('_', ' ') for name in names]

def decode_names_play(name_df):
    """
    Get fullnames by concatenating names from player file into a list"""
    fullnames = []
    for i in range(len(name_df['first_name'])):
        fname_list = name_df['first_name'].iloc[i].split()                          # split (multiple) first names into list
        sname = name_df['second_name'].iloc[i]                                      # get the last name
        name = ' '.join(fname_list)                                                 # sep all fnames by whitespace
        name += ' ' + sname                                                         # separate first names from last name w whitespace
        decoded_name = name.encode('raw_unicode_escape').decode('utf-8')            # decode because names are double encoded in dataset
        fullnames.append(decoded_name)
    return fullnames

def decode_fullnames_gw(names):
    """Formats fullnames in game week files of szns >=19"""
    return [name.encode('raw_unicode_escape').decode('utf-8') for name in names]

def assign_id():
    """Assigns unique field identifiers to player 0 thru n-1 across all seasons.
    idmap = {id: fullname}, w ID formed using fullname"""
    id = 0
    idmap = {}
    for szn in range(cfg.start_season, cfg.end_season+1):
        name_df = load('play', szn, cols=['first_name', 'second_name'])         
        fullnames = decode_names_play(name_df)                              # get all the full names of all players in that season
        for player in fullnames:                  
            if player not in set(idmap):                                    # if the player has not been given an ID yet
                idmap[player] = id                                          # assign id to full name   
                id += 1
    return idmap

def order_ids(idmap, names):
    """Uses id map generated from the player files and orders them for insertion in gw files.
    Full names in map are matched to each line in the gw files"""
    ids = []
    for player in names:
        if player in idmap:                     # check if player has an id
            ids.append(idmap[player])           # add id to list
        else:                                   # if player has no id, throw error
            print(player)
            raise Exception
    return ids

def add_uniq_team_code(team_df):
    """Assigns each team a unique code across szns. DF is passed by ref"""
    uniq_teams = list(set(team_df['team_name']))                    # get list of teams with no duplicate                       
    rev_uniq_map = dict(list(enumerate(uniq_teams)))                # assign ids to them
    uniq_map = dict((v,k) for k,v in rev_uniq_map.items())          # reverse keys and values
    team_df['uniq_code'] = None
    for team in team_df['team_name']:                               # for each team
        condition = (team_df['team_name'] == team)                  # find all occurences in df which match that team
        team_df.loc[condition, 'uniq_code'] = uniq_map[team]        # replace positions in new col

def get_team_codes(szn, old_codes, team_df):
    """Params:
    An array of old codes from the 'opponent_team' col of the gw_df or player_df for that szn
    A team_df with the season, old codes for that season and new codes
    Returns array of rows for the gw_df with new codes corresponding to old codes."""
    rows_in_szn = team_df.loc[team_df['season'] == f'20{szn}-{szn+1}']  # isolate rows of relevant season
    new_codes = []
    for _, old_code in enumerate(old_codes):
        new_code = rows_in_szn.loc[rows_in_szn['team'] == old_code].iloc[0,2]           # the new code is at index [0,2]
        new_codes.append(new_code)
    return new_codes

def process_players(idmap, team_df, szn):
    """Process player files"""
    player_df = load('play', szn, cols=['id', 'first_name', 'second_name', 
                                              'element_type', 'team'])
    names = decode_names_play(player_df[['first_name', 'second_name']])
    ids = order_ids(idmap, names)                                                       # get ids in order of names list
    player_df['name'] = names
    player_df['id'] = ids
    team_codes = get_team_codes(szn, player_df['element_type'],                          
                                  team_df[['season', 'team','uniq_code']])              # get array of team codes for player file
    player_df['team'] = team_codes  
    player_df = player_df.rename(columns={'element_type': 'pos'})                       # rename pos col for clarity                             
    new_player_df = player_df[['id', 'name', 'team', 'pos']]                            # take only relevant cols
    save('play', new_player_df, szn)
    print(f'Processed players')


def process_gws(idmap, team_df, szn):
    """Process gameweek files"""
    gw_df = load('gw', szn, cols=['name', 'element', 'total_points', 
                                      'value', 'GW', 'opponent_team'])                  # current model only uses a few fields
    names = gw_df['name'].tolist()                                                      # make df into list
    if szn == 18 or szn == 19:                                                          # if gw names have undesired postfix
        names = remove_postfix(names)                                                   # remove them
    if szn >= 19:
        names = decode_fullnames_gw(names)                                    
    names = rm_underscores(names)                                                       # remove unwanted underscores for ease of matching
    ids = order_ids(idmap, names)                                                       # get ids in order of names list
    gw_df['id'] = ids                                                                   # add them to the dataframe 
    opp_codes = get_team_codes(szn, gw_df['opponent_team'], 
                                  team_df[['season', 'team','uniq_code']])              # get array of new unique opp team codes for gw file
    gw_df['opponent'] = opp_codes
    new_gw_df = gw_df[['GW', 'id', 'value', 'opponent', 'total_points']]                # save only relevant cols
    save('gw', new_gw_df, szn)                                    
    print(f'Processed game weeks')

def main():
    """Conducts preprocessing of raw data"""
    idmap = assign_id()                                                                 # assign unique id to players across szns
    team_df = load('teams')                                                             # requires all cols 
    add_uniq_team_code(team_df)                                                         # give each team a unique code (df passed by ref)
    save('teams', team_df)                                                              # save so that uniq codes are not changed in next run
    for szn in range(cfg.start_season, cfg.end_season+1):  
        print('----------------------')
        print(f'Starting season {szn}')
        print('----------------------')
        process_players(idmap, team_df, szn)
        process_gws(idmap, team_df, szn)
        print(f'Done with season {szn}-{szn+1}')

if __name__ == '__main__':
    main()



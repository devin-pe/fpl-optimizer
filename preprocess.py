import numpy as np
import pandas as pd
from collections import Counter
from clean import load
from player import player
from enum import Enum

"""Formation"""
class Pos(Enum):
    GK = 0
    DEF = 1
    MID = 2
    FWD = 3

def count_pos(positions):
    """Conducts simple sanity check 
    Counts the number of players in each pos from squad"""
    if len(positions) != 11:
        return False
    
    count = Counter(positions)
    n_gk = count['1']
    n_def = count['2']
    n_mid = count['3']
    n_fwd = count['4']

    return (n_gk, n_def, n_mid, n_fwd)

def check_team_comp(positions):
    """Ensures starting-11 composition is legal following
    1 GK, 3-5 DEF, 2-5 MID, 1-3 FWD"""
    n_gk, n_def, n_mid, n_fwd = count_pos(positions)
    return (n_gk == 1 and 3 <= n_def <= 5 and 2 <= n_mid <= 5 and 
            1 <= n_fwd <= 3 and n_gk+n_def+n_mid+n_fwd == 11)

def sample_players(player_df, pos, n=1):
    player_df_by_pos = player_df[player_df['pos'] == pos]           
    team_players_df = player_df_by_pos.sample(n=n)               
    return team_players_df

def select_players_randomly(player_df, compo):
    """Selects 11 rows which contain the given labels for position (vals 1-4)"""
    team_df = pd.DataFrame(columns=player_df.columns)
    for i, n in enumerate(compo):
        team_players_df = sample_players(player_df, i+1, n)                     # i+1 bc pos starts at 1, not 0
        team_df = pd.concat([team_df, team_players_df], ignore_index=True)      # concat dataframes with diff n of rows
    return team_df

def get_gw_df(gw, gw_df, player_df, team_df, replace=True):
    """Selects rows which contain the ids in the player row list for the correct gw
    Modifies team_df"""
    gw_df_week = gw_df[(gw_df['GW'] == gw)]                                     # filter by gameweek 
    start_gw_df = pd.DataFrame(columns=gw_df_week.columns)                      # init empty df to contain gw data of starting 11
    for i, row in team_df.iterrows():                                        
        gw_row = gw_df_week[gw_df_week['id'] == row['id']]                      # filter Series obj by ID
        while gw_row.empty and replace:                                         # replace row until a valid player is found
                                                                                # (i.e. one who is playing that gameweek)
            row = sample_players(player_df, row.loc['pos'])                     # replace invalid player by player w same pos                    
            gw_row = gw_df_week[gw_df_week['id'] == row['id'].values[0]]        # filter DF object by ID
            team_df.iloc[i] = row                                               # replace invalid player row 
        start_gw_df = start_gw_df.append(gw_row)
    return start_gw_df

def calc_past_pts(gw, gw_df, player_df, player_rows):
    """Gets a total of all points in the past gameweeks for each player specified in the ids list"""
    past_pts = [0] * len(player_rows)
    for w in range(1, gw):                                    # GW starts at 1, up to last week
        rows = get_gw_df(w, gw_df, player_df, player_rows, replace=False)
        for i, row in enumerate(rows):
            if not row.empty:
                past_pts[i] += row.iloc[0,4]
    return past_pts

def select_player_stats(gw, player_df, gw_df, compo):
    """Selects players until a list of current players are found
    Returns metrics from player_df, gw_df and total_points"""           
    team_df = select_players_randomly(player_df, compo)         # select player rows at random from df
    new_gw_df = get_gw_df(gw, gw_df, player_df, team_df)    # get current gw rows for those players
    past_pts = calc_past_pts(gw, gw_df, player_df, team_df) # get past points for the whole season  
    return team_df, new_gw_df, past_pts

def gen_compo():
    """Returns a list with 4 elements, wherein the number of players 
    for each of 4 positions is specified"""
    min_def = 3; min_mid = 2; min_fwd = 1
    compo = [1, min_def, min_mid, min_fwd]                          # set position minimums
    pos_to_fill = [Pos.DEF, Pos.MID, Pos.FWD]

    # Populate team with 11 random players
    while sum(compo) < 11:
        pos = np.random.choice(pos_to_fill)                         # choose random pos
        compo[pos.value] += 1                                       # add player to pos
    
    # Modify compo so position maximums are not exceeded
    while compo[Pos.DEF.value] > 5:
        pos = np.random.choice([Pos.MID, Pos.FWD])                  # choose random pos remaining
        compo[pos.value] += 1                                       # add player to pos
        compo[Pos.DEF.value] -= 1                                   # remove from defenders
    
    while compo[Pos.MID.value] > 5:
        pos = np.random.choice([Pos.DEF, Pos.FWD])                  # choose random pos remaining
        compo[pos.value] += 1                                       # add player to pos
        compo[Pos.MID.value] -= 1                                   # remove from midfielders
    
    while compo[Pos.FWD.value] > 3:
        pos = np.random.choice([Pos.DEF, Pos.MID])                  # choose random pos remaining
        compo[pos.value] += 1                                       # add player to pos
        compo[Pos.FWD.value] -= 1                                   # remove from forwards

    return compo


def init_team(gw, gw_df, player_df):
    """Initialize team to be used to create team objects (individuals in EA)"""
    # Choose team comp (n of players in each pos)

    # New strategy: generate player by player until team is full, exclude pos once max reached
    compo = gen_compo()
    team_df, new_gw_df, past_pts = select_player_stats(gw, player_df, gw_df, compo)   # get all necessary stats

    # Init players
    players = []
    print('p rows: ', len(team_df))
    print('gw rows: ', len(new_gw_df))
    print('past_pts: ', len(past_pts))
    for i, (p_row, gw_row) in enumerate(zip(team_df, new_gw_df)):
        assert p_row.iloc[0,0] == gw_row.iloc[0,1], 'should be in the same order by ID'
        p = player(p_row, gw_row, past_pts[i])
        players.append(p)
    return players # temp



    
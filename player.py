class player:
    def __init__(self, play_row, gw_row, past_pts):
        """Params: 
        player_row: a row from the player df
        gw_row: a row for the players in player_df in the GW
        past_pts: past points for each player"""

        # player file
        self.id = play_row.iloc[0,0]  
        self.name = play_row.iloc[0,1]     
        self.team = play_row.iloc[0,2]                                
        self.pos = play_row.iloc[0,3]   
         
         # gw file
        self.opp = gw_row.iloc[0,3]
        self.val = gw_row.iloc[0,2]
        self.past_pts = past_pts

    def update_val(self, val):
        self.val = val

    def get_id(self):
        return self.id
    
    def get_name(self):
        return self.name

    def get_team(self):
        return self.team

    def get_pos(self):
        return self.pos

    def get_val(self):
        return self.val
    
    def get_past_pts(self):
        return self.past_pts

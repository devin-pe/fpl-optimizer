from preprocess import check_team_comp, init_team


class team:
    def __init__(self, gw, szn, players=None):
        """Params:
        players: a list of 11 player objects"""
        if len(players) != 11:
            raise Exception(f'Players {len(players)} != 11')
        if not players:
            init_team(gw, szn)
            check_team_comp([p.get_pos() for p in players])
        
        self._team = players
        self._total_val = sum([player.get_val() for player in players])



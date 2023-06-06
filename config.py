"""HYPERPARAMETER CONFIGURATIONS"""

'''main.py hyperparameters'''
start_season        = 16    # the first season where data is available is 16-17
end_season          = 21    # the first season where data is available is 21-22
n_teams_per_szn     = 20    # the number of teams in the PL per season
n_teams_formed      = 25    # the number of teams formed every gameweek, adding more increases convergence but is more computationally intensive

'''train.py hyperparameters'''
learning_rate    = 0.00001     # how fast we learn - this one seems to work good from trial and error
batch_size       = 32          # how many memories we sample from memory while learning


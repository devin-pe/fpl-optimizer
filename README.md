# FPL Optimizer

The purpose of this library is to predict the best 11-man squad of every gameweek in the [Fantasy Premier League](https://fantasy.premierleague.com) game. 

## Description

In Fantasy Premier League (FPL), players choose an 11-man squad every gameweek. Their players are attributed points based on their performance. The formation of a team is dependent on a few constraints. There is a minimum and maximum number of players in each position allowed on the team; a team may not contain more than 3 players from the same club; the budget for the team is £100 million. There are other rules which add more complexity to the game such as transfers and chips but this simplified program does not address that.

With the aim of maximizing a team's score, a genetic algorithm is employed to generate 25 optimal teams for every past gameweek. These squads are used as predicted output for an ANN. The ANN takes as input the chosen 11 player-price-opponent tuples (more dimensions may be added later) and compares them to the optimal team selected by the genetic algorithm.

## Getting Started

The program is still under development and not functional at this point in time.

### Prerequisites

- Python 3.8+

- Libraries

Install the required packages via pip:

```
$ pip install -r requirements.txt
```


import numpy as np
import pandas as pd


def simple_simulation(plus_ev_df):
    start_amount = 1000
    bet_amount = 25  # bet amount is from kelley criteria = W - ((1 - W)/R)
    for i, row in plus_ev_df.iterrows():
        if row.Bet_Type == row.home:
            win = (bet_amount * (1 + row.implied_win_home)) - bet_amount
            lose = bet_amount
            if row.score_home > row.score_away:
                start_amount = start_amount + win
            elif row.score_home < row.score_away:
                start_amount = start_amount - lose
            else:
                pass

        elif row.Bet_Type == row.away:
            win = (bet_amount * (1 + row.implied_win_away)) - bet_amount
            lose = bet_amount
            if row.score_away > row.score_home:
                start_amount = start_amount + win
            elif row.score_away < row.score_home:
                start_amount = start_amount - lose
            else:
                pass
        print(start_amount)
    return start_amount

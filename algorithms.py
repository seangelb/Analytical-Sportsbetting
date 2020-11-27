import pandas as pd
import numpy as np


def implied_probability(ml):  # get implied probability for moneyline
    if ml == 100:
        return .5
    elif ml > 0:
        return round((100 / (ml + 100)), 6)  # if positive ML
    else:
        return round((abs(ml) / (abs(ml) + 100)), 6)  # if negative ML


def ml_probabilities(self, df):
    df['implied_win_home'] = df['home_ML'].apply(lambda x: self.implied_probability(x))
    df['implied_win_away'] = df['away_ML'].apply(lambda x: self.implied_probability(x))
    df['total_implied_prob'] = df['implied_win_away'] + df['implied_win_home']
    return df


# P(WIN|PS) = Historical Win % of Teams with Point Spread
# We theorize that a team at point spread PS will win at the same rate at which historical teams at spread PS have won.
def win_percent(df): #thinking maybe do bayesian stats over time... time series for backtesting.
    dict_win = {}
    for num in [x * 0.5 for x in range(1, 60)]:
        win_count = 0
        df_spread = df[df['spread_favorite'] == (-1 * num)]
        total = 0
        for row in df_spread.itertuples():  # intertuples much faster than regular array
            difference = 0
            if row.team_favorite_id == row.home:
                fav = (-1 * row.spread_favorite) + row.score_home
                difference = fav - row.score_away
                if difference > 0:  # if x + spread > y then add to win group
                    win_count += 1
            elif row.team_favorite_id == row.away:
                fav = (-1 * row.spread_favorite) + row.score_away
                difference = fav - row.score_home
                if difference > 0:
                    win_count += 1
            if difference == 0:
                total = total - 1  # remove one since wash
            total += 1  # iterate
        if total != 0:
            dict_win[-num] = np.round((win_count / total), 6)
    return dict_win


# need to still incorporate epsilon rate -> will need to run montecarlo to determine
def plus_ev_games(win_dict, df, min_ev, largest_spread_fav=-100):  # spread is always in negative
    # defeault largest spread fav and unlimited
    plus_ev = pd.DataFrame()
    for i, row in df.iterrows():  # iterate through each row in the dataframe
        spread = row.spread_favorite
        implied_ml = 0.01
        if row.team_favorite_id == row.home:
            fav_implied_ml = row.implied_win_home
            favorite = row.home
            underdog_implied_ml = row.implied_win_away
            underdog = row.away
        elif row.team_favorite_id == row.away:
            fav_implied_ml = row.implied_win_away
            favorite = row.away
            underdog_implied_ml = row.implied_win_home
            underdog = row.home

        # to prevent %/0 error
        if spread == 0:
            spread = -1

        fav_ev = round((win_dict[spread] * fav_implied_ml) - (1 - win_dict[spread]), 6)
        underdog_ev = round((1 - win_dict[spread] * underdog_implied_ml) - (win_dict[spread]), 6)

        # determine which has a create EV
        ev = 0
        if fav_ev >= underdog_ev:
            ev = fav_ev
            row['EV'] = ev
            row['Bet Type'] = favorite

        else:
            ev = underdog_ev
            row['EV'] = ev
            row['Bet Type'] = underdog
        # print(ev)
        if (ev >= min_ev) & (spread > largest_spread_fav):
            # print(ev)

            plus_ev = plus_ev.append(row)
    return plus_ev

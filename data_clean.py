import pandas as pd
import numpy as np


def clean_data(scores, teams, date):
    df_spread = pd.read_csv(scores)
    df_spread['schedule_date'] = pd.to_datetime(df_spread['schedule_date'])  # date
    df = df_spread[df_spread['schedule_date'] > date]  # "2009-9-10" # games starting in week 1 of 2009
    #df = df_spread[df_spread['schedule_date'] < "2009-11-07"]  #test

    df_teams = pd.read_csv(teams)
    df_name_id = df.merge(df_teams, left_on="team_home", right_on="team_name")
    df_name_id = df_name_id[['team_name', 'team_id']]
    df_name_id = df_name_id.drop_duplicates()

    # change all team names to team_ids for both home and away
    merged = df.merge(df_name_id, left_on='team_home', right_on='team_name', how='left')
    merged = merged.drop(labels=['team_home', 'team_name'], axis=1)
    merged = merged.rename(columns={'team_id': 'home'})

    merged = merged.merge(df_name_id, left_on='team_away', right_on='team_name', how='left')
    merged = merged.drop(labels=['team_away', 'team_name'], axis=1)
    merged = merged.rename(columns={'team_id': 'away'})

    merged = merged.reset_index(drop=True)
    return merged


def make_simple(df):  # main dataset
    df = df[['schedule_date', 'home', 'score_home', 'away', 'score_away', 'team_favorite_id', 'spread_favorite']]
    df = df.dropna(
        subset=['schedule_date', 'home', 'score_home', 'away', 'score_away', 'team_favorite_id', 'spread_favorite'])
    return df


def remove_misc_teams(bad_data, df_ml):  # used on ml df. Removes random teams from dataset
    df_ml = df_ml[~df_ml['team'].isin(bad_data)]
    df_ml = df_ml[~df_ml['opp_team'].isin(bad_data)]
    return df_ml


# def add_city_to_team(df_teams):  # do this before calling funct add_names_to_teams. Allows for key value pair between df_teams and df_ml
#     df_teams[['City', "Name"]] = df_teams["team_name"].str.rsplit(" ", 1, expand=True)
#     df_teams = df_teams.drop("Name", axis=1)
#     return df_teams


# def add_names_to_teams(df_teams, team_names, copy_team):
#     for i in range(0, len(team_names)):
#         df_teams = df_teams.append(df_teams[df_teams['team_name'] == copy_team[i]], ignore_index=True)
#         last_index = df_teams.index[-1]
#         df_teams.loc[last_index, 'team_name'] = team_names[i]
#     return df_teams


def add_team_id_to_ml(df_ml, df_teams):
    df_ml = df_ml.merge(df_teams[['team_id', 'City']], left_on='team', right_on='City', how='left')
    df_ml = df_ml.drop_duplicates()
    return df_ml


def export_df_ml_to_csv(
        df_ml):  # I need to do this to create a keyvalue pair w/ nfl_team so I can then connect to the main dataframe
    df = df_ml['opp_team'].unique()
    np.savetxt("1df_ml_teams.csv", df, fmt='%s')


def add_ml_team_id(self, df_ml, df_teams,
                   csvfile="team_key_value_pairs.csv"):  # changes team names to team id by merged df_ml, df_team, and a key value pair table
    df_kv = pd.read_csv(csvfile)
    df_ml = df_ml.merge(df_kv, left_on='team', right_on='team', how='left')
    df_ml = df_ml.merge(df_teams[['team_name', 'team_id']], left_on='team_name', right_on='team_name', how='left')
    df_ml = df_ml.drop("team_name", axis=1)
    df_ml = df_ml.merge(df_kv, left_on='opp_team', right_on='team', how='left')
    df_ml = df_ml.merge(df_teams[['team_name', 'team_id']], left_on='team_name', right_on='team_name', how='inner')
    df_ml = df_ml.drop(["team_x", "opp_team", "team_name", "team_y", "team_name"], axis=1)
    df_ml = df_ml.rename(columns={"team_id_x": "home", "team_id_y": "away"})

    df_ml['moneyline'] = df_ml[['ml_PIN', 'ml_FD', 'ml_HER', 'ml_BVD', 'ml_BOL', 'ml_BET', 'ml_BOD']].values.tolist()
    df_ml = df_ml.drop(['ml_PIN', 'ml_FD', 'ml_HER', 'ml_BVD', 'ml_BOL', 'ml_BET', 'ml_BOD'], axis=1)
    df_ml['moneyline'] = df_ml['moneyline'].apply(lambda x: [i for i in x if i == i])
    df_ml['moneyline'] = df_ml['moneyline'].apply(lambda x: self.median_split_special_case(x))
    # use median of the lines for the moneyline (will try out other methods in future). This is mostly for backtesting.
    df_ml_home = df_ml[
        df_ml['H/A'] == 'home']  # I would do if postive, highest ML, if negative, then number closest to 0.
    df_ml_away = df_ml[df_ml['H/A'] == 'away']
    df_ml = df_ml_home.merge(df_ml_away[['key', 'moneyline']], on="key")
    df_ml = df_ml.rename(columns={"moneyline_x": "home_ML", "moneyline_y": "away_ML"})
    df_ml['date'] = pd.to_datetime(df_ml['date'], format='%Y%m%d')  # date
    return df_ml


def add_spread_team_id(df_ml, df_teams,
                       csvfile="team_key_value_pairs.csv"):  # changes team names to team id by merged df_ml, df_team, and a key value pair table
    df_kv = pd.read_csv(csvfile)
    df_ml = df_ml.merge(df_kv, left_on='team', right_on='team', how='left')
    df_ml = df_ml.merge(df_teams[['team_name', 'team_id']], left_on='team_name', right_on='team_name', how='left')
    df_ml = df_ml.drop("team_name", axis=1)
    df_ml = df_ml.merge(df_kv, left_on='opp_team', right_on='team', how='left')
    df_ml = df_ml.merge(df_teams[['team_name', 'team_id']], left_on='team_name', right_on='team_name', how='inner')
    df_ml = df_ml.drop(["team_x", "opp_team", "team_name", "team_y", "team_name"], axis=1)
    df_ml = df_ml.rename(columns={"team_id_x": "home", "team_id_y": "away"})

    df_ml['spread'] = df_ml[['pinnacle_line', '5dimes_line', 'heritage_line', 'betonline_line', 'bet365_line',
                             'bodog_line']].values.tolist()
    df_ml = df_ml.drop(['pinnacle_line', '5dimes_line', 'heritage_line', 'betonline_line', 'bet365_line', 'bodog_line'],
                       axis=1)
    df_ml['spread'] = df_ml['spread'].apply(lambda x: [float(i) for i in x if is_float(i)])
    df_ml['spread'] = df_ml['spread'].apply(lambda x: [i for i in x if i == i])
    df_ml['spread'] = df_ml['spread'].apply(lambda x: np.median(x)) #try min
    df_ml_home = df_ml[
        df_ml['H/A'] == 'home']  # I would do if postive, highest ML, if negative, then number closest to 0.
    df_ml_away = df_ml[df_ml['H/A'] == 'away']

    df_ml = df_ml_home.merge(df_ml_away[['key', 'spread']], on="key")
    df_ml = df_ml.rename(columns={"spread_x": "home_spread", "spread_y": "away_spread"})
    df_ml['date'] = pd.to_datetime(df_ml['date'], format='%Y%m%d')

    df_ml['spread_favorite'] = np.where(df_ml['home_spread'] >= df_ml['away_spread'], df_ml['away_spread'],
                                        df_ml['home_spread'])
    df_ml['team_favorite_id'] = np.where(df_ml['home_spread'] >= df_ml['away_spread'], df_ml['away'], df_ml['home'])
    df_ml = df_ml[['date', 'home', 'away', 'team_favorite_id', 'spread_favorite']]
    return df_ml


def update_spreads(df, df_spread_update): #updated spread since 2009. Still need a way to get score
    df_spread_update = df.merge(df_spread_update,left_on=['schedule_date', 'home', 'away'], right_on=['date', 'home', 'away'], how='left')
    df_spread_update = df_spread_update.drop(['spread_favorite_x', 'team_favorite_id_x', 'date'], axis = 1)
    df_spread_update = df_spread_update.rename(columns={"spread_favorite_y" : "spread_favorite", "team_favorite_id_y" : "team_favorite_id"})
    return df_spread_update



def merge_spread(df, df_ml):
    # merge df_ml to df_spread
    df = df.merge(df_ml[['date', 'home', 'away', 'home_spread', 'away_spread']],
                  left_on=['schedule_date', 'home', 'away'],
                  right_on=['date', 'home', 'away'], how='left')
    df = df.drop('date', axis=1)
    return df


def is_float(n):  # checks to see if number is a real number else returns false
    try:
        float(n)
        return True
    except ValueError:
        return False


def median_split_special_case(
        ml_list):  # rare case so I won't worry too much abt theory. If even and +/- equal then median breaks
    if len(ml_list) % 2 == 0:  # very inefficient
        count_postive = 0
        count_negative = 0
        for num in ml_list:
            if num > 0:
                count_postive += 1
            else:
                count_negative += 1
        if count_negative == count_postive:
            return np.median(np.abs(ml_list))
        return np.median(ml_list)


def merge(df, df_ml): #adds moneyline info to the dataset
    # merge df_ml to df_spread
    df = df.merge(df_ml[['date', 'home', 'away', 'home_ML', 'away_ML']], left_on=['schedule_date', 'home', 'away'],
                  right_on=['date', 'home', 'away'], how='left')
    df = df.drop('date', axis=1)
    return df


def do(self):
    bad_data = ['NFC', 'AFC', 'Team Rice', 'Team Sanders', 'Team Carter', 'Team Irvin']

    df = self.clean_data("spreadspoke_scores.csv", "nfl_teams.csv", "2009-9-10")
    df = self.make_simple(df)
    df_teams = pd.read_csv("nfl_teams.csv")
    df_ml = pd.read_csv("NFL_moneylines.csv")
    df_spread = pd.read_csv("NFL_spread_since2009.csv")
    df_spread = self.remove_misc_teams(bad_data, df_spread)
    df_spread = self.add_spread_team_id(df_spread, df_teams)

    df = self.update_spreads(df, df_spread) #update dataframe to most up-to-date spreads since 2009
    df_ml = self.remove_misc_teams(bad_data, df_ml)
    df_ml = self.add_ml_team_id(self, df_ml, df_teams)
    df = self.merge(df, df_ml)
    df = df.dropna()  # drops around 300 games with NA values (SBR did not record them for some reason)
    return df

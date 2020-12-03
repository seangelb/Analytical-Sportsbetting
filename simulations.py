import numpy as np
import pandas as pd
import datetime


def historic_win_set(ey, em, ed, sy=2009, sm=9, sd=10):
    start_date = datetime.date(sy, sm, sd)
    end_date = datetime.date(ey, em, ed)
    return start_date, end_date


# https://www.investopedia.com/terms/w/win-loss-ratio.asp
# w_l is a trader's number of winning trades relative to the number of osing trades.
# A negative Kelly criterion means that the bet is not favored by the model and should be avoided.
# start amount is for starting amount
def kelly_criterion(win_dict, fav_spread, bet_type, team_favorite_id, win_loss):
    if bet_type == team_favorite_id:
        W = win_dict[fav_spread]
    elif fav_spread == 0:
        W = .5
    else:
        W = 1 - win_dict[fav_spread]
    R = sum(win_loss) / len(win_loss)
    K = W - ((1 - W) / R)
    return K / 100


def amount_to_bet(current_amount, kelly_percent):
    amount = round(current_amount * kelly_percent)
    return amount


class Simulations:
    def __init__(self, start_amount, ev, max_spread, start_date, end_date):
        # self.epsilon = epsilon
        self.bet = 0
        self.ev = ev
        self.max_spread = max_spread
        self.start_date = start_date
        self.end_date = end_date
        self.current_ev = start_amount
        self.current_amount = start_amount
        self.win_loss = []
        for x in range(0, 60):  # 30 moving average start w/ 66% track record
            if x % 3 == 0:
                self.win_loss.append(0)
            else:
                self.win_loss.append(1)

    def simple_simulation(self, plus_ev_df, win_dict):
        # bet_amount = 25 #bet amount is from kelley criteria = W - ((1 - W)/R)
        for i, row in plus_ev_df.iterrows():
            # print(row)
            # kelly_percent = kelly_criterion(win_dict, row.spread_favorite, row.Bet_Type, row.team_favorite_id,self.win_loss)
            # # print(kelly_percent)
            # if (kelly_percent < 0) | (self.max_spread >= row.spread_favorite):
            #     continue  # go to next game
            if self.max_spread >= row.spread_favorite:
                continue
            # bet_amount = round(amount_to_bet(self.current_amount, kelly_percent), 2)
            bet_amount = 10
            lose = bet_amount

            # bet_amount = 25
            # print(bet_amount)
            if (row.Bet_Type == row.home) | (row.Bet_Type == row.away):
                self.current_ev += (bet_amount * row.EV)
                self.bet += 1  # count number of bets made

            if row.Bet_Type == row.home:
                # see how I should be winning vs theoretical EV wise.
                win = (
                                  bet_amount / row.implied_win_home) - bet_amount  # you win difference in implied rate + initial bet
                if row.score_home > row.score_away:  # if you win you make the implied moneyline
                    self.win_loss.append(1)
                    self.win_loss.pop(0)  # increase w/l ratio
                    self.current_amount += win

                elif row.score_home < row.score_away:  # if you lose you lose your bet amount
                    self.current_amount -= lose
                    self.win_loss.append(0)
                    self.win_loss.pop(0)  # increase w/l ratio

            elif row.Bet_Type == row.away:  # same theory but for the other side
                win = (bet_amount / row.implied_win_away) - bet_amount
                if row.score_away > row.score_home:
                    self.current_amount += win
                    self.win_loss.append(1)
                    self.win_loss.pop(0)  # increase w/l ratio
                elif row.score_away < row.score_home:
                    self.current_amount -= lose
                    self.win_loss.append(0)
                    self.win_loss.pop(0)  # increase w/l ratio
            #print(bet_amount, self.current_amount, round((bet_amount * row.EV),2), self.current_ev)

    def simulate_v2(self, df_historic_win, df_ml, algorithms):
        # more advanced simulation with win_data updating everyday
        delta = datetime.timedelta(days=1)
        while self.start_date <= self.end_date:  # simulate for everyday between the start date and end date, might update to only gamedays
            check_date = str(self.start_date)
            games_today = df_ml[df_ml['schedule_date'] == check_date]
            if len(games_today) == 0:  # check to see if values in row else pass
                # print(len(games_today))
                self.start_date += delta  # iterate date
                continue
            else:
                win_data = df_historic_win[
                    df_historic_win['schedule_date'] < check_date]  # create win_df for days before the event
                win_dict = algorithms.win_percent(win_data)  # update win percentage dict based on days before
                self.start_date += delta  # iterate through date
                plus_ev_df = algorithms.plus_ev_games(win_dict, games_today, self.ev,
                                                      largest_spread_fav=self.max_spread)  # choose largest spread, ev. Should just be games for today
                # self.current_amount += self.simple_simulation(plus_ev_df, win_dict)
                self.simple_simulation(plus_ev_df, win_dict)

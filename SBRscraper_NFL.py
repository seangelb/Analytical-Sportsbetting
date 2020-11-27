# import socket
# import socks
import requests
from bs4 import BeautifulSoup
import datetime
from datetime import date
import time
from pandas import DataFrame
from pathlib import Path

def soup_url(type_of_line, tdate=str(date.today()).replace('-', '')):
    ## get html code for odds based on desired line type and date

    web_url = dict()
    web_url['ML'] = 'money-line/'
    web_url['RL'] = 'pointspread/'
    web_url['total'] = 'totals/'
    url_addon = web_url[type_of_line]

    url = 'https://classic.sportsbookreview.com/betting-odds/nfl-football/' + url_addon + '?date=' + tdate
    now = datetime.datetime.now()
    raw_data = requests.get(url)
    soup_big = BeautifulSoup(raw_data.text, 'html.parser')
    #print(soup_big.prettify())
    try:
        soup = soup_big.find_all('div', id='OddsGridModule_16')[0]
    except:
        soup = None
    timestamp = time.strftime("%H:%M:%S")
    return soup, timestamp


def replace_unicode(string):
    return string.replace(u'\xa0', ' ').replace(u'\xbd', '.5')


def parse_and_write_data(soup, date, not_ML=True):
    ## Parse HTML to gather line data by book
    def book_line(book_id, line_id, homeaway):
        ## Get Line info from book ID
        line = soup.find_all('div', attrs={'class': 'el-div eventLine-book', 'rel': book_id})[line_id].find_all('div')[
            homeaway].get_text().strip()
        #print(line)
        return line

    '''
    BookID  BookName
    238     Pinnacle
    19      5Dimes
    93      Bookmaker
    1096    BetOnline
    169     Heritage
    123     BetDSI
    999996  Bovada
    139     Youwager
    999991  SIA
    
    43 bet365
    92 Bodog
    '''
    if not_ML:
        df = DataFrame(
            columns=('key', 'date', 'time', 'H/A',
                     'team', 'opp_team',
                     'pinnacle_line', 'pinnacle_odds',
                     '5dimes_line', '5dimes_odds',
                     'heritage_line', 'heritage_odds',
                     'bovada_line', 'bovada_odds',
                     'betonline_line', 'betonline_odds',
                     'bet365_line', 'bet365_odds',
                     'bodog_line', 'bodog_odds'))
    else:
        df = DataFrame(
            columns=('key', 'date', 'time', 'H/A',
                     'team', 'opp_team', 'pinnacle', '5dimes',
                     'heritage', 'bovada', 'betonline', 'bet365', 'bodog'))
    counter = 0
    try:
        number_of_games = len(soup.find_all('div', attrs={'class': 'el-div eventLine-rotation'}))
    except:
        number_of_games = 0
    if number_of_games != 0:
        team_counter = 0
        for i in range(0, number_of_games):
            A = []
            H = []
            #print(str(i + 1) + '/' + str(number_of_games))
            team_A = ""
            team_H = ""

            ## Gather all useful data from unique books
            # consensus_data =  soup.find_all('div', 'el-div eventLine-consensus')[i].get_text()
            team_A = soup.find_all('span', attrs={'class': 'team-name'})[team_counter].text
            team_counter = team_counter + 1
            team_H = soup.find_all('span', attrs={'class': 'team-name'})[team_counter].text
            team_counter = team_counter + 1

            # print(info_A)
            # print("space-------------------------------")
            # print(team_A)
            ## get line/odds info for unique book. Need error handling to account for blank data
            def try_except_book_line(id, i, x):
                try:
                    return book_line(id, i, x)
                except IndexError:
                    return ''

            pinnacle_A = try_except_book_line('238', i, 0)
            fivedimes_A = try_except_book_line('19', i, 0)
            heritage_A = try_except_book_line('169', i, 0)
            bovada_A = try_except_book_line('999996', i, 0)
            betonline_A = try_except_book_line('1096', i, 0)
            bet365_A = try_except_book_line('43', i, 0)
            bodog_A = try_except_book_line('92', i, 0)

            pinnacle_H = try_except_book_line('238', i, 1)
            fivedimes_H = try_except_book_line('19', i, 1)
            heritage_H = try_except_book_line('169', i, 1)
            bovada_H = try_except_book_line('999996', i, 1)
            betonline_H = try_except_book_line('1096', i, 1)
            bet365_H = try_except_book_line('43', i, 1)
            bodog_H = try_except_book_line('92', i, 1)

            A.append(str(date) + '_' + team_A.replace(u'\xa0', ' ') + '_' + team_H.replace(u'\xa0', ' '))
            A.append(date)
            A.append(time)
            A.append('away')
            A.append(team_A)
            A.append(team_H)
            if not_ML:
                pinnacle_A = replace_unicode(pinnacle_A)
                pinnacle_A_line = pinnacle_A[:pinnacle_A.find(' ')]
                pinnacle_A_odds = pinnacle_A[pinnacle_A.find(' ') + 1:]
                A.append(pinnacle_A_line)
                A.append(pinnacle_A_odds)
                fivedimes_A = replace_unicode(fivedimes_A)
                fivedimes_A_line = fivedimes_A[:fivedimes_A.find(' ')]
                fivedimes_A_odds = fivedimes_A[fivedimes_A.find(' ') + 1:]
                A.append(fivedimes_A_line)
                A.append(fivedimes_A_odds)
                heritage_A = replace_unicode(heritage_A)
                heritage_A_line = heritage_A[:heritage_A.find(' ')]
                heritage_A_odds = heritage_A[heritage_A.find(' ') + 1:]
                A.append(heritage_A_line)
                A.append(heritage_A_odds)
                bovada_A = replace_unicode(bovada_A)
                bovada_A_line = bovada_A[:bovada_A.find(' ')]
                bovada_A_odds = bovada_A[bovada_A.find(' ') + 1:]
                A.append(bovada_A_line)
                A.append(bovada_A_odds)
                betonline_A = replace_unicode(betonline_A)
                betonline_A_line = betonline_A[:betonline_A.find(' ')]
                betonline_A_odds = betonline_A[betonline_A.find(' ') + 1:]
                A.append(betonline_A_line)
                A.append(betonline_A_odds)
                bet365_A = replace_unicode(bet365_A)
                bet365_A_line = bet365_A[:bet365_A.find(' ')]
                bet365_A_odds = bet365_A[bet365_A.find(' ') + 1:]
                A.append(bet365_A_line)
                A.append(bet365_A_odds)
                bodog_A = replace_unicode(bodog_A)
                bodog_A_line = bodog_A[:bodog_A.find(' ')]
                bodog_A_odds = bodog_A[bodog_A.find(' ') + 1:]
                A.append(bodog_A_line)
                A.append(bodog_A_odds)
            else:
                A.append(replace_unicode(pinnacle_A))
                A.append(replace_unicode(fivedimes_A))
                A.append(replace_unicode(heritage_A))
                A.append(replace_unicode(bovada_A))
                A.append(replace_unicode(betonline_A))
                A.append(replace_unicode(bet365_A))
                A.append(replace_unicode(bodog_A))
            H.append(str(date) + '_' + team_A.replace(u'\xa0', ' ') + '_' + team_H.replace(u'\xa0', ' '))
            H.append(date)
            H.append(time)
            H.append('home')
            H.append(team_H)
            H.append(team_A)

            if not_ML:
                pinnacle_H = replace_unicode(pinnacle_H)
                pinnacle_H_line = pinnacle_H[:pinnacle_H.find(' ')]
                pinnacle_H_odds = pinnacle_H[pinnacle_H.find(' ') + 1:]
                H.append(pinnacle_H_line)
                H.append(pinnacle_H_odds)
                fivedimes_H = replace_unicode(fivedimes_H)
                fivedimes_H_line = fivedimes_H[:fivedimes_H.find(' ')]
                fivedimes_H_odds = fivedimes_H[fivedimes_H.find(' ') + 1:]
                H.append(fivedimes_H_line)
                H.append(fivedimes_H_odds)
                heritage_H = replace_unicode(heritage_H)
                heritage_H_line = heritage_H[:heritage_H.find(' ')]
                heritage_H_odds = heritage_H[heritage_H.find(' ') + 1:]
                H.append(heritage_H_line)
                H.append(heritage_H_odds)
                bovada_H = replace_unicode(bovada_H)
                bovada_H_line = bovada_H[:bovada_H.find(' ')]
                bovada_H_odds = bovada_H[bovada_H.find(' ') + 1:]
                H.append(bovada_H_line)
                H.append(bovada_H_odds)
                betonline_H = replace_unicode(betonline_H)
                betonline_H_line = betonline_H[:betonline_H.find(' ')]
                betonline_H_odds = betonline_H[betonline_H.find(' ') + 1:]
                H.append(betonline_H_line)
                H.append(betonline_H_odds)
                bet365_H = replace_unicode(bet365_H)
                bet365_H_line = bet365_H[:bet365_H.find(' ')]
                bet365_H_odds = bet365_H[bet365_H.find(' ') + 1:]
                H.append(bet365_H_line)
                H.append(bet365_H_odds)
                bodog_H = replace_unicode(bodog_H)
                bodog_H_line = bodog_H[:bodog_H.find(' ')]
                bodog_H_odds = bodog_H[bodog_H.find(' ') + 1:]
                H.append(bodog_H_line)
                H.append(bodog_H_odds)
            else:
                H.append(replace_unicode(pinnacle_H))
                H.append(replace_unicode(fivedimes_H))
                H.append(replace_unicode(heritage_H))
                H.append(replace_unicode(bovada_H))
                H.append(replace_unicode(betonline_H))
                H.append(replace_unicode(bet365_H))
                H.append(replace_unicode(bodog_H))
            ## Take data from A and H (lists) and put them into DataFrame
            df.loc[counter] = ([A[j] for j in range(len(A))])
            df.loc[counter + 1] = ([H[j] for j in range(len(H))])
            counter += 2
    return df


def select_and_rename(df, text):
    ## Select only useful column names from a DataFrame
    ## Rename column names so that when merged, each df will be unique 
    if text[-2:] == 'ml':
        df = df[['key', 'time', 'team', 'opp_team',
                 'pinnacle', '5dimes', 'heritage', 'bovada', 'betonline', 'bet365', 'bodog']]
        ## Change column names to make them unique
        df.columns = ['key', text + '_time', 'team', 'opp_team',
                      text + '_PIN', text + '_FD', text + '_HER', text + '_BVD', text + '_BOL']
    else:
        df = df[['key', 'time', 'team', 'opp_team',
                 'pinnacle_line', 'pinnacle_odds',
                 '5dimes_line', '5dimes_odds',
                 'heritage_line', 'heritage_odds',
                 'bovada_line', 'bovada_odds',
                 'betonline_line', 'betonline_odds',
                 'bet365_line', 'bet365_odds',
                     'bodog_line', 'bodog_odds']]

        df.columns = ['key', text + '_time', 'team', 'opp_team',
                      text + '_PIN_line', text + '_PIN_odds',
                      text + '_FD_line', text + '_FD_odds',
                      text + '_HER_line', text + '_HER_odds',
                      text + '_BVD_line', text + '_BVD_odds',
                      text + '_BOL_line', text + '_BOL_odds',
                      text + '_BET_line', text + '_BET_odds',
                      text + '_BOD_line', text + '_BOD_odds']
    return df


def blank_out_df(df, text):
    ## Select only useful column names from a DataFrame
    ## Rename column names so that when merged, each df will be unique 
    if text[-2:] == 'ml':
        df = df[['key', 'time', 'team', 'opp_team',
                 'pinnacle', '5dimes', 'heritage', 'bovada', 'betonline', 'bet365', 'bodog']]
        ## Change column names to make them unique
        df.columns = ['key', text + '_time', 'team', 'opp_team',
                      text + '_PIN', text + '_FD', text + '_HER', text + '_BVD', text + '_BOL', text + '_BET', text + '_BOD']

        df[text + '_PIN'] = ""
        df[text + '_FD'] = ""
        df[text + '_HER'] = ""
        df[text + '_BVD'] = ""
        df[text + '_BOL'] = ""
        df[text + '_BET'] = ""
        df[text + '_BOD'] = ""

    else:
        df = df[['key', 'time', 'team', 'opp_team',
                 'pinnacle_line', 'pinnacle_odds',
                 '5dimes_line', '5dimes_odds',
                 'heritage_line', 'heritage_odds',
                 'bovada_line', 'bovada_odds',
                 'betonline_line', 'betonline_odds']]
        df.columns = ['key', text + '_time', 'team', 'opp_team',
                      text + '_PIN_line', text + '_PIN_odds',
                      text + '_FD_line', text + '_FD_odds',
                      text + '_HER_line', text + '_HER_odds',
                      text + '_BVD_line', text + '_BVD_odds',
                      text + '_BOL_line', text + '_BOL_odds']

        df[text + '_PIN_line'] = ""
        df[text + '_FD_line'] = ""
        df[text + '_HER_line'] = ""
        df[text + '_BVD_line'] = ""
        df[text + '_BOL_line'] = ""
        df[text + '_PIN_odds'] = ""
        df[text + '_FD_odds'] = ""
        df[text + '_HER_odds'] = ""
        df[text + '_BVD_odds'] = ""
        df[text + '_BOL_odds'] = ""

    return df


def main():
    ## Get today's lines

    startDate = date(2000,9,10)
    closeDate = date(2009,9,1)
    difference = closeDate - startDate
    difference = int(difference.days) + 1

    for numb in range(1,difference):
        todays_date = startDate + datetime.timedelta(days=1) + datetime.timedelta(days=numb)
        todays_date = str(todays_date).replace('-', '')
        ## change todays_date to be whatever date you want to pull in the format 'yyyymmdd'
        ## One could force user input and if results in blank, revert to today's date.
        # todays_date = '20140611'

        ## store BeautifulSoup info for parsing
        try:
            soup_ml, time_ml = soup_url('ML', todays_date)
            #print("getting today's MoneyLine " + todays_date)

        except:
            print("couldn't get today's moneyline :(")

        # try:
        #     soup_tot, time_tot = soup_url('total', todays_date)
        #     print("getting today's totals " + todays_date)
        # except:
        #     print("couldn't get today's totals :(")

        #### Each df_xx creates a data frame for a bet type
        #print("writing today's MoneyLine " + todays_date)
        df_ml = parse_and_write_data(soup_ml, todays_date, not_ML=False)

    ## Change column names to make them unique
        df_ml.columns = ['key', 'date', 'ml_time', 'H/A', 'team', 'opp_team',
                         'ml_PIN', 'ml_FD', 'ml_HER', 'ml_BVD', 'ml_BOL', 'ml_BET', 'ml_BOD']
        df_ml = df_ml.drop(['ml_time'], axis=1)


        ## Merge all DataFrames together to allow for simple printout
        write_df = df_ml

        my_file = Path("NFL_moneylines_2000_2009.csv")
        if my_file.is_file():
            with open('NFL_moneylines_2000_2009.csv', 'a') as f:
                write_df.to_csv(f, header=False, index=False)
        else:
            with open('NFL_moneylines_2000_2009.csv', 'a') as f:
                write_df.to_csv(f, header=True, index=False)



if __name__ == '__main__':
    main()
    print("complete :)")

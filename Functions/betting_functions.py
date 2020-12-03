import pandas as pd
import numpy as np
sys.path.insert(0, '/NHL_Game_Prediction/Functions/')
from functions.app_functions import *

''' Returns specific season'''
def extract_season(game, season):
    return game[(game['season'] == season)]

''' Specialized function to convert game times to EST'''
def convert_to_EST(game):
    game[['date_time_GMT']] = pd.to_datetime(game['date_time_GMT'])
    game[['date_time_GMT']] = game['date_time_GMT'].apply(lambda x: convert_timezones(x))
    return game

''' Helper function to convert to EST'''
def convert_timezones(time):
    return time.astimezone('EST')

''' Formats years correctly'''
def add_year(date, season):
    if int(date) > 1000:
        return season[:2] + ':' + date[:2] + ':' + date[2:]
    else:
        return season[2:] + ':' + date[:2] + ':' + date[2:]

''' Convert the odds datetime column to the correct format'''
def convert_odds_date(odds, season):
    odds['season'] = season
    odds[['Date']] = odds['Date'].astype(str)
    odds[['Date']] = odds['Date'].str.zfill(4)
    odds['cvt_date'] = odds.apply(lambda x: add_year(x.Date, x.season), axis=1)
    odds['cvt_date'] = pd.to_datetime(odds['cvt_date'], format='%y:%m:%d')
    return odds

''' Preprocess the odds data'''
def preprocess_odds_dataframe(odds):
    away = odds.loc[(odds['VH']=='V')]
    home = odds.loc[(odds['VH']=='H')]
    home = home.iloc[1:].reset_index(drop=True)
    away = away.iloc[1:].reset_index(drop=True)
    even = odds.iloc[::2]
    odd = odds.iloc[1::2]

    indexes = np.arange(0,len(odds)/2)
    even['index'] = indexes
    odd['index'] = indexes
    combined = even.merge(odd, on='index')
    combined = combined[['Team_x','Team_y', 'Open_x','Open_y','index','cvt_date_y']]
    combined = combined.rename(columns={'Team_x':'away_team', 'Team_y':'home_team', 'Open_x':'away_odds', 'Open_y':'home_odds', 'cvt_date_y':'date_time'})
    combined = combined.sort_values(by=['date_time','away_team'])
    return combined

'''Cleans the names of teams to match the odds df'''
def clean_team_names(y_pred):

    y_pred['away_team'] = y_pred['away_team'].str.replace(" ","")
    y_pred['home_team'] = y_pred['home_team'].str.replace(" ","")

    y_pred['away_team'] = y_pred['away_team'].str.replace("StLouis","St.Louis")
    y_pred['home_team'] = y_pred['home_team'].str.replace("StLouis","St.Louis")

    return y_pred

'''Merges the odds dataframe with predictions made by the model'''
def merge_odds_predictions(y_pred, odds):

    y_pred['date_time'] = y_pred['date_time_GMT'].dt.date
    y_pred['date_time'] = pd.to_datetime(y_pred['date_time'])

    merged = y_pred.merge(odds, left_on=['date_time','home_team','away_team'], right_on=['date_time','home_team','away_team'])

    return merged

'''Matches the games bet on by the selective model to all the games in the test set. This helps identify
periods of time that the selective model didn't bet, and allows for later graphing and comparisons between
model'''
def process_selective_model(games_bet_on_selective, profit_time_selective, total_wager_time_selective, merged):

    games_bet_on_selective['profit'] = profit_time_selective
    games_bet_on_selective['total_wager_time'] = total_wager_time_selective
    games_bet_on_selective = games_bet_on_selective[['date_time', 'home_team','away_team','profit','total_wager_time']].sort_values(by='date_time')
    temp_merged = merged[['date_time','home_team','away_team']].sort_values(by='date_time')
    join = temp_merged.merge(games_bet_on_selective, on=['date_time','home_team','away_team'],how='outer')
    join['profit'][0] = 0
    join['total_wager_time'][0] = 0
    join = join.fillna(method='ffill')
    join['rate_of_return'] = join['profit']/join['total_wager_time']
    join = join.fillna(0)

    return join

'''Makes baseline predictions - bets on the favourite of every game'''
def predict_baseline(predictions):
    
    predictions['baseline_pred'] = predictions.apply(lambda x: baseline_helper(x.away_odds, x.home_odds), axis=1)
    
    profit = 0
    profit_time = []
    total_bet_time = []
    total_bet = 0
    games_bet_on = []
    
    for i in range(len(predictions)):
        
        game = predictions.iloc[i]
        result = game['target']
        guess = game['baseline_pred']
            
        if guess == 0:
            
            odds = game['home_odds']
        
        else:
            
            odds = game['away_odds']
            
        if (result == guess):
                
            if odds > 0:
                    
                total_bet += 100
                profit += odds
                
            else:
                    
                total_bet += abs(odds)
                profit += 100
            
        else:
                
            if odds > 0:
                    
                total_bet += 100
                profit -= 100
                    
            else:
                    
                total_bet += abs(odds)
                profit += odds
        
        profit_time.append(profit)
        total_bet_time.append(total_bet)
        games_bet_on.append(game)
        
        
    return profit, total_bet, profit_time, total_bet_time, games_bet_on

'''Helper function for the baseline'''
def baseline_helper(away_odds, home_odds):
    if home_odds < away_odds:
        return 0
    else:
        return 1

'''Makes predictions based on the model. Bets on every game but based on the models predictions'''
def make_money(predictions):
    
    profit = 0
    profit_time = []
    total_bet_time = []
    total_bet = 0
    games_bet_on = []
    
    for i in range(len(predictions)):
        
        game = predictions.iloc[i]
        result = game['target']
        guess = game['pred']
            
        if guess == 0:
            
            odds = game['home_odds']
        
        else:
            
            odds = game['away_odds']
            
        if (result == guess):
                
            if odds > 0:
                    
                total_bet += 100
                profit += odds
                
            else:
                    
                total_bet += abs(odds)
                profit += 100
            
        else:
                
            if odds > 0:
                    
                total_bet += 100
                profit -= 100
                    
            else:
                    
                total_bet += abs(odds)
                profit += odds
        
        profit_time.append(profit)
        total_bet_time.append(total_bet)
        games_bet_on.append(game)
        
        
    return profit, total_bet, profit_time, total_bet_time, games_bet_on

'''Helper function to determine game days'''
def get_betting_dates(merged):
    merged['date_time'] = merged['date_time_GMT'].dt.date.astype('str')
    dates = list(merged['date_time'].astype('str').unique())
    
    return dates

'''Selective betting predictions. Bets on 1 game each day there are games, selecting the highest Expected Profit.
This is computed based on the model's confidence combined with the odds'''
def selective_betting(merged, dates):
    total_wager = 0
    profit = 0
    profit_time = []
    bets_placed = []
    
    games_bet_on = pd.DataFrame()

    for day in dates:
        games = merged[(merged['date_time'] == day)]
        games = games.reset_index(drop=True)
        profit_games, bad_games, to_bet = get_positive_profit(games)

        if to_bet == False:
            continue
        game_list = list(profit_games.index)
        profit_games = profit_games.reset_index()
        profit_games = profit_games.rename(columns={'level_0':'Unnamed: 0'})
        #print(day)

        confidence = abs(profit_games['home_prob'][0] - profit_games['away_prob'][0])

        if confidence > 0.2:
            bet = 200

        else:
            bet = 100

        wager = calc_bets(bet, len(profit_games), profit_games, game_list)

        if wager['pred'][0] == wager['target'][0]:    

            profit += wager['win_profit'][0]

        else:

            profit -= 100
        
        profit_time.append(profit)  
        total_wager += bet
        bets_placed.append(total_wager) 
        games_bet_on = games_bet_on.append(wager)
        
    return profit, profit_time, bets_placed, total_wager, games_bet_on
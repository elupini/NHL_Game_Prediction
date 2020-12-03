import numpy as np
import pandas as pd

'''Calculates the best betting strategy based on amount, risk level, games selected, and the model's predictions'''
def calc_bets(amount, risk, game_idx, df, moneyline):

    expected_profit_dict = {}
    expected_loss_dict = {}

    for index in game_idx:

        prediction = df.iloc[index]['pred']
        home_odds = moneyline.iloc[index]['home_odds']
        away_odds = moneyline.iloc[index]['away_odds']
        home_prob = df.iloc[index]['home_prob']
        away_prob = df.iloc[index]['away_prob']
        expected_profit = 0
        expected_loss = 0
        #return [home_odds, away_odds]

        # If we predicted favoured team

        if prediction == 0:

            expected_loss = away_prob * amount
        
        else:

            expected_loss = home_prob * amount

        if (home_odds > 0) & (away_odds < 0):

            expected_profit = (amount * (home_odds/100) * home_prob) + (amount * (100/away_odds) * away_prob)

        elif (home_odds > 0) & (away_odds > 0):

            expected_profit = (amount * (home_odds/100) * home_prob) - (amount * (away_odds/100) * away_prob)

        elif (away_odds > 0) & (home_odds < 0):

            expected_profit = (amount * abs(100/home_odds) * home_prob) - (amount * (away_odds/100) * away_prob)

        elif (away_odds < 0) & (home_odds < 0):

            expected_profit = (amount * abs(100/home_odds) * home_prob) + (amount * (100/away_odds) * away_prob)

        if prediction == 1:

            expected_profit = expected_profit * -1

        expected_profit_dict[index] = expected_profit
        expected_loss_dict[index] = expected_loss

    #return expected_profit_dict, expected_loss_dict
    wager = {}

    if risk == 2:
        max_profit = max(expected_profit_dict.values())
        max_profit_key = 0

        for key, _ in expected_profit_dict.items():
            if expected_profit_dict[key] == max_profit:
                max_profit_key = key

        if df.iloc[max_profit_key]['pred'] == 0:
            wager['betting_team'] = df.iloc[max_profit_key]['home_team']
            wager['other_team'] = df.iloc[max_profit_key]['away_team']
            wager['confidence'] = df.iloc[max_profit_key]['home_prob']

            if moneyline.iloc[max_profit_key]['home_odds'] > 0:
                wager['profit'] = abs(moneyline.iloc[max_profit_key]['home_odds']/100) * amount
            else:
                wager['profit'] = abs(100/moneyline.iloc[max_profit_key]['home_odds']) * amount

        else:
            wager['betting_team'] = df.iloc[max_profit_key]['away_team']
            wager['other_team'] = df.iloc[max_profit_key]['home_team']
            wager['confidence'] = df.iloc[max_profit_key]['away_prob']

            if moneyline.iloc[max_profit_key]['away_odds'] > 0:
                wager['profit'] = abs(moneyline.iloc[max_profit_key]['away_odds']/100) * amount
            else:
                wager['profit'] = abs(100/moneyline.iloc[max_profit_key]['away_odds']) * amount
        
        wager['amount'] = amount

    elif risk == 1:
        min_loss = min(expected_loss_dict.values())
        min_loss_key = 0

        for key, _ in expected_loss_dict.items():
            if expected_loss_dict[key] == min_loss:
                min_loss_key = key


        if df.iloc[min_loss_key]['pred'] == 0:
            wager['betting_team'] = df.iloc[min_loss_key]['home_team']
            wager['other_team'] = df.iloc[min_loss_key]['away_team']
            wager['confidence'] = df.iloc[min_loss_key]['home_prob']

            if moneyline.iloc[min_loss_key]['home_odds'] > 0:
                wager['profit'] = abs(moneyline.iloc[min_loss_key]['home_odds']/100) * amount
            else:
                wager['profit'] = abs(100/moneyline.iloc[min_loss_key]['home_odds']) * amount

        else:
            wager['betting_team'] = df.iloc[min_loss_key]['away_team']
            wager['other_team'] = df.iloc[min_loss_key]['home_team']
            wager['confidence'] = df.iloc[min_loss_key]['away_prob']

            if moneyline.iloc[min_loss_key]['away_odds'] > 0:
                wager['profit'] = abs(moneyline.iloc[min_loss_key]['away_odds']/100) * amount
            else:
                wager['profit'] = (abs(100/moneyline.iloc[min_loss_key]['away_odds']) * amount)
        
        wager['amount'] = amount

    return wager


''' Creates a text based classification of confidence in the prediction'''
def classify_matchup(df):

    df['difference'] = abs(df['home_prob'] -  df['away_prob'])

    df['text_prediction'] = df.apply(lambda x: classify_matchup_helper(x.difference, x.home_team, x.away_team, x.pred), axis=1)

    return df

''' Helper function for the matchup classifier'''
def classify_matchup_helper(diff, home, away, pred):

    diff = diff * 100

    if pred == 0:
        
        winner = home

    else:
        winner = away

    if diff <= 10:

        return f'Tiny advantage for {winner}'
    
    elif (diff > 10) & (diff <= 20):

        return f"Small advantage for {winner}"

    elif (diff > 20) & (diff <= 35):

        return f"Clear advantage for {winner}"

    else:

        return f"Overwhelming advantage for {winner}"


''' Extracts number from specifically formatted string'''
def extract_num(box_string):

    num = box_string.split("_")

    return int(num[1])

'''Gets the expected profit, based on model confidence and odds'''
def get_expected_profit(home_odds, away_odds, home_prob, away_prob, pred):
    
    if (home_odds > 0) & (away_odds < 0):

        expected_profit = ((home_odds/100) * home_prob) + ((100/away_odds) * away_prob)

    elif (home_odds > 0) & (away_odds > 0):

        expected_profit = ((home_odds/100) * home_prob) - ((away_odds/100) * away_prob)

    elif (away_odds > 0) & (home_odds < 0):

        expected_profit = (abs(100/home_odds) * home_prob) - ((away_odds/100) * away_prob)

    elif (away_odds < 0) & (home_odds < 0):

        expected_profit = (abs(100/home_odds) * home_prob) + ((100/away_odds) * away_prob)

    if pred == 1:

        expected_profit = expected_profit * -1
    
    return expected_profit

'''Calculates how the wager should be split between games'''
def calc_bets(amount, risk, games, game_list):
    
    profit_games = pd.DataFrame()

    for idx in game_list:
        temp = games[(games['Unnamed: 0']==idx)]
        profit_games = profit_games.append(temp)

    profit_games['wager'] = amount
    
    profit_games = profit_games[(profit_games['expected_profit'] > 0)].sort_values(by='expected_profit', ascending=False).reset_index(drop=True)
    
    risk_list = np.arange(len(profit_games),0,-1)
    
    profit_games['wager'] = amount * (profit_games.iloc[:risk_list[risk-1]]['expected_profit']/sum(profit_games.iloc[:risk_list[risk-1]]['expected_profit']))
    
    profit_games[['betting_team', 'other_team', 'confidence']] = profit_games.apply(lambda x: get_betting_info(x.pred, x.home_team, x.away_team, x.home_prob, x.away_prob), axis=1)
    
    profit_games['win_profit'] = profit_games.apply(lambda x: get_win_profit(x.pred, x.home_odds, x.away_odds, x.wager), axis=1)
    
    return profit_games.dropna()

'''Gets the total possible profit'''
def get_win_profit(pred, home_odds, away_odds, wager):
    
    if pred == 1:
        
        if away_odds > 0:
            
            return abs((away_odds/100) * wager)
        
        else:
            
            return abs((100/away_odds) * wager)
    
    else:
        
        if home_odds > 0:
            
            return abs((home_odds/100) * wager)
        
        else:
            
            return abs((100/home_odds) * wager)

'''Gets games that have positive expected profit, returns df of bad games that aren't worth betting on'''
def get_positive_profit(games, bet=True):
    
    games['expected_profit'] = games.apply(lambda x: get_expected_profit(x.home_odds, x.away_odds, x.home_prob, x.away_prob, x.pred), axis=1)
    
    profit_games = games[(games['expected_profit'] > 0)].sort_values(by='expected_profit', ascending=False)
    bad_games = games[(games['expected_profit'] <= 0)]

    if len(profit_games) == 0:
        bet = False

    return profit_games, bad_games, bet

'''Helper function'''
def get_betting_info(pred, home_team, away_team, home_prob, away_prob):
    
    if pred == 1:
        betting_team = away_team
        other_team = home_team
        confidence = away_prob
    else:
        betting_team = home_team
        other_team = away_team
        confidence = home_prob
    
    return pd.Series([betting_team, other_team, confidence])

''' Helper function'''
def get_losing_probability(home_prob, away_prob):

    return min(home_prob, away_prob)

'''Returns prob of losing a game'''
def get_prob_lose(games):

    games['prob_lose'] = games.apply(lambda x: get_losing_probability(x.home_prob, x.away_prob), axis=1)
    prob_losing = np.prod(games['prob_lose'])

    return prob_losing
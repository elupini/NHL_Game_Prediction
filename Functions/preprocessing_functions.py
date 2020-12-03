import pandas as pd

''' Adds a date column to the goalie stats'''
def add_dates(game, goalie_stats):

    game_dates = game[['game_id','date_time_GMT']]
    goalie_stats_dates = goalie_stats.merge(game_dates, on='game_id')

    return goalie_stats_dates
    
''' Gets starting goaltenders for each game'''
def get_starting_goalies(game, goalie_stats, game_shifts):

    goalies = pd.DataFrame(columns=['game_id','player_id','team_id'])

    team_ids = goalie_stats.team_id.unique()

    for team in team_ids:
        games = goalie_stats[(goalie_stats['team_id']==team)]
        games_merge = games.merge(game_shifts, on=['game_id','player_id'])
        games_merge['starting_goalie'] = games_merge.apply(lambda x: starting_goalie_helper(x.period, x.shift_start), axis=1)
        starting_goalies = games_merge[(games_merge['starting_goalie']==True)][['game_id','player_id','team_id']]
        
        goalies = goalies.append(starting_goalies)

    main_merge = game.merge(goalies, left_on=['game_id','away_team_id'], right_on=['game_id','team_id'])
    main_merge = main_merge.rename(columns={'player_id':'away_starting_goalie'})
    main_merge = main_merge.merge(goalies, left_on=['game_id','home_team_id'], right_on=['game_id','team_id'])
    main_merge = main_merge.rename(columns={'player_id':'home_starting_goalie'})

    return main_merge

''' Helper function for the starting goaltenders'''
def starting_goalie_helper(period, shift_start):
    
    if (period == 1) & (shift_start == 0):
        return True
    else:
        return False

''' Calculates the rolling averages for goalie stats, given a window size'''
def goalie_rolling_stats(window, game, goalie_data):

    window_str = str(window)

    goalie_ids = goalie_data['player_id'].unique()

    goalie_stats_df = pd.DataFrame(columns=['game_id','player_id','team_id','shots'+window_str,'date_time_GMT', 'saves'+window_str, 'powerPlaySaves'+window_str, 'shortHandedSaves'+window_str, 'evenSaves'+window_str, 'savePercentage'+window_str, 'powerPlaySavePercentage'+window_str, 'evenStrengthSavePercentage'+window_str])

    for goalie in goalie_ids:
        goalie_stats = goalie_data[(goalie_data['player_id']==goalie)].sort_values(by='date_time_GMT')

        goalie_stats['shots'+window_str] = goalie_stats.shots.rolling(window, min_periods=1).mean()
        goalie_stats['saves'+window_str] = goalie_stats.saves.rolling(window, min_periods=1).mean()
        goalie_stats['powerPlaySaves'+window_str] = goalie_stats.powerPlaySaves.rolling(window, min_periods=1).mean()
        goalie_stats['shortHandedSaves'+window_str] = goalie_stats.shortHandedSaves.rolling(window, min_periods=1).mean()
        goalie_stats['evenSaves'+window_str] = goalie_stats.evenSaves.rolling(window, min_periods=1).mean()
        goalie_stats['savePercentage'+window_str] = goalie_stats.savePercentage.rolling(window, min_periods=1).mean()
        goalie_stats['powerPlaySavePercentage'+window_str] = goalie_stats.powerPlaySavePercentage.rolling(window, min_periods=1).mean()
        goalie_stats['evenStrengthSavePercentage'+window_str] = goalie_stats.evenStrengthSavePercentage.rolling(window, min_periods=1).mean()

        goalie_stats[['shots'+window_str, 'saves'+window_str, 'powerPlaySaves'+window_str, 'shortHandedSaves'+window_str, 'evenSaves'+window_str, 'savePercentage'+window_str, 'powerPlaySavePercentage'+window_str, 'evenStrengthSavePercentage'+window_str]] = goalie_stats[['shots'+window_str, 'saves'+window_str, 'powerPlaySaves'+window_str, 'shortHandedSaves'+window_str, 'evenSaves'+window_str, 'savePercentage'+window_str, 'powerPlaySavePercentage'+window_str, 'evenStrengthSavePercentage'+window_str]].shift(periods=1, axis=0)

        goalie_stats = goalie_stats[['game_id','player_id','team_id','date_time_GMT','shots'+window_str, 'saves'+window_str, 'powerPlaySaves'+window_str, 'shortHandedSaves'+window_str, 'evenSaves'+window_str, 'savePercentage'+window_str, 'powerPlaySavePercentage'+window_str, 'evenStrengthSavePercentage'+window_str]]

        goalie_stats_df = goalie_stats_df.append(goalie_stats)

        final_rolling_goalie = rename_goalie(goalie_stats_df, game, window)

    return final_rolling_goalie

''' Renaming helper function for goalie rolling averages'''
def rename_goalie(goalie_stats_df, game, window):

    if window == 5:

        rolling_merge = game.merge(goalie_stats_df, left_on=['game_id','away_starting_goalie'], right_on=['game_id','player_id'])

        rolling_merge = rolling_merge.rename(columns={'shots5':'away_shots_5', 'saves5':'away_saves_5', 'powerPlaySaves5':'away_pps_5', 'shortHandedSaves5':'away_shs_5', 'evenSaves5':'away_evenSaves_5', 'savePercentage5':'away_save%_5', 'powerPlaySavePercentage5':'away_ppsave%_5', 'evenStrengthSavePercentage5':'away_evenSave%_5'})

        rolling_merge = rolling_merge.merge(goalie_stats_df, left_on=['game_id','home_starting_goalie'], right_on=['game_id','player_id'])

        rolling_merge = rolling_merge.rename(columns={'shots5':'home_shots_5', 'saves5':'home_saves_5', 'powerPlaySaves5':'home_pps_5', 'shortHandedSaves5':'home_shs_5', 'evenSaves5':'home_evenSaves_5', 'savePercentage5':'home_save%_5', 'powerPlaySavePercentage5':'home_ppsave%_5', 'evenStrengthSavePercentage5':'home_evenSave%_5'})
    
    elif window == 10:

        rolling_merge = game.merge(goalie_stats_df, left_on=['game_id','away_starting_goalie'], right_on=['game_id','player_id'])

        rolling_merge = rolling_merge.rename(columns={'shots10':'away_shots_10', 'saves10':'away_saves_10', 'powerPlaySaves10':'away_pps_10', 'shortHandedSaves10':'away_shs_10', 'evenSaves10':'away_evenSaves_10', 'savePercentage10':'away_save%_10', 'powerPlaySavePercentage10':'away_ppsave%_10', 'evenStrengthSavePercentage10':'away_evenSave%_10'})

        rolling_merge = rolling_merge.merge(goalie_stats_df, left_on=['game_id','home_starting_goalie'], right_on=['game_id','player_id'])

        rolling_merge = rolling_merge.rename(columns={'shots10':'home_shots_10', 'saves10':'home_saves_10', 'powerPlaySaves10':'home_pps_10', 'shortHandedSaves10':'home_shs_10', 'evenSaves10':'home_evenSaves_10', 'savePercentage10':'home_save%_10', 'powerPlaySavePercentage10':'home_ppsave%_10', 'evenStrengthSavePercentage10':'home_evenSave%_10'})

    elif window == 40:

        rolling_merge = game.merge(goalie_stats_df, left_on=['game_id','away_starting_goalie'], right_on=['game_id','player_id'])

        rolling_merge = rolling_merge.rename(columns={'shots40':'away_shots_40', 'saves40':'away_saves_40', 'powerPlaySaves40':'away_pps_40', 'shortHandedSaves40':'away_shs_40', 'evenSaves40':'away_evenSaves_40', 'savePercentage40':'away_save%_40', 'powerPlaySavePercentage40':'away_ppsave%_40', 'evenStrengthSavePercentage40':'away_evenSave%_40'})

        rolling_merge = rolling_merge.merge(goalie_stats_df, left_on=['game_id','home_starting_goalie'], right_on=['game_id','player_id'])

        rolling_merge = rolling_merge.rename(columns={'shots40':'home_shots_40', 'saves40':'home_saves_40', 'powerPlaySaves40':'home_pps_40', 'shortHandedSaves40':'home_shs_40', 'evenSaves40':'home_evenSaves_40', 'savePercentage40':'home_save%_40', 'powerPlaySavePercentage40':'home_ppsave%_40', 'evenStrengthSavePercentage40':'home_evenSave%_40'})

    elif window == 82:

        rolling_merge = game.merge(goalie_stats_df, left_on=['game_id','away_starting_goalie'], right_on=['game_id','player_id'])

        rolling_merge = rolling_merge.rename(columns={'shots82':'away_shots_82', 'saves82':'away_saves_82', 'powerPlaySaves82':'away_pps_82', 'shortHandedSaves82':'away_shs_82', 'evenSaves82':'away_evenSaves_82', 'savePercentage82':'away_save%_82', 'powerPlaySavePercentage82':'away_ppsave%_82', 'evenStrengthSavePercentage82':'away_evenSave%_82'})

        rolling_merge = rolling_merge.merge(goalie_stats_df, left_on=['game_id','home_starting_goalie'], right_on=['game_id','player_id'])

        rolling_merge = rolling_merge.rename(columns={'shots82':'home_shots_82', 'saves82':'home_saves_82', 'powerPlaySaves82':'home_pps_82', 'shortHandedSaves82':'home_shs_82', 'evenSaves82':'home_evenSaves_82', 'savePercentage82':'home_save%_82', 'powerPlaySavePercentage82':'home_ppsave%_82', 'evenStrengthSavePercentage82':'home_evenSave%_82'})

    return rolling_merge

'''Creates differentials for goalie stats'''
def get_goalie_differentials(merged_df):

    merged_df['shots_5_avg'] =  merged_df['away_shots_5'] - merged_df['home_shots_5']
    merged_df['saves_5_avg'] =  merged_df['away_saves_5'] - merged_df['home_saves_5']
    merged_df['pps_5_avg'] =  merged_df['away_pps_5'] - merged_df['home_pps_5']
    merged_df['shs_5_avg'] =  merged_df['away_shs_5'] - merged_df['home_shs_5']
    merged_df['evenSaves_5_avg'] =  merged_df['away_evenSaves_5'] - merged_df['home_evenSaves_5']
    merged_df['save%_5_avg'] =  merged_df['away_save%_5'] - merged_df['home_save%_5']
    merged_df['ppsave%_5_avg'] =  merged_df['away_ppsave%_5'] - merged_df['home_ppsave%_5']
    merged_df['evenSave%_5_avg'] =  merged_df['away_evenSave%_5'] - merged_df['home_evenSave%_5']

    merged_df['shots_10_avg'] =  merged_df['away_shots_10'] - merged_df['home_shots_10']
    merged_df['saves_10_avg'] =  merged_df['away_saves_10'] - merged_df['home_saves_10']
    merged_df['pps_10_avg'] =  merged_df['away_pps_10'] - merged_df['home_pps_10']
    merged_df['shs_10_avg'] =  merged_df['away_shs_10'] - merged_df['home_shs_10']
    merged_df['evenSaves_10_avg'] =  merged_df['away_evenSaves_10'] - merged_df['home_evenSaves_10']
    merged_df['save%_10_avg'] =  merged_df['away_save%_10'] - merged_df['home_save%_10']
    merged_df['ppsave%_10_avg'] =  merged_df['away_ppsave%_10'] - merged_df['home_ppsave%_10']
    merged_df['evenSave%_10_avg'] =  merged_df['away_evenSave%_10'] - merged_df['home_evenSave%_10']

    merged_df['shots_40_avg'] =  merged_df['away_shots_40'] - merged_df['home_shots_40']
    merged_df['saves_40_avg'] =  merged_df['away_saves_40'] - merged_df['home_saves_40']
    merged_df['pps_40_avg'] =  merged_df['away_pps_40'] - merged_df['home_pps_40']
    merged_df['shs_40_avg'] =  merged_df['away_shs_40'] - merged_df['home_shs_40']
    merged_df['evenSaves_40_avg'] =  merged_df['away_evenSaves_40'] - merged_df['home_evenSaves_40']
    merged_df['save%_40_avg'] =  merged_df['away_save%_40'] - merged_df['home_save%_40']
    merged_df['ppsave%_40_avg'] =  merged_df['away_ppsave%_40'] - merged_df['home_ppsave%_40']
    merged_df['evenSave%_40_avg'] =  merged_df['away_evenSave%_40'] - merged_df['home_evenSave%_40']

    return merged_df

''' Gets winner for specific situations'''
def get_outcome_by_team(home_id, away_id, target, team_id):
    
    if (home_id == team_id) & (target == 0):
        return 1
    elif (home_id == team_id) & (target == 1):
        return 0   
    elif (away_id == team_id) & (target == 1):
        return 1
    elif (away_id == team_id) & (target == 0):
        return 0
    
    return

''' Helper function for head to head features'''
def head_2_head_helper(home_id, away_id, head_2_head, team_id):
    
    if home_id == team_id:
        return head_2_head
    else:
        return 1-head_2_head

''' Helper function for getting head to head features'''
def get_both_teams(home, away):
    team_1 = min(home, away)
    team_2 = max(home, away)
    return str(team_1) + ' ' + str(team_2)

''' Get head to head matchup features'''
def get_head_2_head(df, window):
    
    str_window = str(window)
    
    df['both_ids'] = df.apply(lambda x: get_both_teams(x.home_team_id, x.away_team_id), axis=1)
    matchups = list(df['both_ids'].unique())
    
    temp_df = pd.DataFrame()
    
    for pair in matchups:
        
        matchup = df.loc[(df['both_ids']== pair)].sort_values(by='date_time')
        ids = matchup['home_team_id'].unique()
        matchup['relevant_id'] = ids[0]
        matchup['head_2_head'] = matchup.apply(lambda x: get_outcome_by_team(x.home_team_id, x.away_team_id, x.target, x.relevant_id), axis=1)
        matchup['head_2_head_test'] = (matchup.head_2_head.rolling(window, min_periods=1).mean())
        matchup[['head_2_head_test']] = matchup[['head_2_head_test']].shift(periods=1, axis=0)
        matchup['head_2_head_home_p'+str_window] = matchup.apply(lambda x: head_2_head_helper(x.home_team_id, x.away_team_id, x.head_2_head_test, x.relevant_id), axis=1)
        
        temp_df = temp_df.append(matchup)
    
    temp_df = temp_df.drop(columns = ['relevant_id', 'head_2_head', 'head_2_head_test'])
    
    return temp_df

''' Gets target variable'''
def get_outcome(outcome):
    if 'home win' in outcome:
        return 0
    elif 'away win' in outcome:
        return 1
    else:
        return 'unknown'

''' Removes seasons that are too old to be relevant or affected by the lockout'''
def select_seasons(season_list, df):

    df = df[df.season.isin(season_list)]

    return df

''' Remove games that are missing enough data to model accurately'''
def remove_missing_games(df, stats):
    game_id = list(df.game_id)
    reduced_game_id = list(stats.index)
    difference = list(set(game_id) - set(reduced_game_id))
    to_remove = df[df['game_id'].isin(difference)].index
    complete_games = df.drop(df.index[to_remove])
    return complete_games

''' Formats stats dataframe to include game information in single rows'''
def combine_home_away(game_teams_stats):
    
    even = [i for i in range(0, len(game_teams_stats), 2)]
    odd = [i for i in range(1, len(game_teams_stats), 2)]
    
    away_games = game_teams_stats.iloc[even]
    home_games = game_teams_stats.iloc[odd]
    
    single_games = pd.merge(away_games, home_games, on='game_id')
    
    names = {'team_id_x':'away_team_id', 'won_x':'away_win', 'settled_in_x':'result',
       'head_coach_x':'away_head_coach', 'goals_x':'away_goals', 'shots_x':'away_shots', 'hits_x':'away_hits', 'pim_x':'away_pim',
       'powerPlayOpportunities_x':'away_PPO', 'powerPlayGoals_x':'away_PPG',
       'faceOffWinPercentage_x':'away_faceoff_win_pct', 'giveaways_x':'away_giveaways', 'takeaways_x':'away_takeaways', 'team_id_y':'home_team_id',
       'won_y':'home_win', 'head_coach_y':'home_head_coach', 'goals_y':'home_goals', 'shots_y':'home_shots',
       'hits_y':'home_hits', 'pim_y':'home_pim', 'powerPlayOpportunities_y':'home_PPO', 'powerPlayGoals_y':'home_PPG',
       'faceOffWinPercentage_y':'home_faceoff_win_pct', 'giveaways_y':'home_giveaways', 'takeaways_y':'home_takeaways'}
    
    single_games = single_games.rename(columns=names)
    
    return single_games

''' Rolling stats helper function'''
def align_stats_away(home_id, away_id, home_stat, away_stat, team_id):
    
    if home_id == team_id:
        return away_stat
        
    elif away_id == team_id:
        return home_stat
    
    return

''' Rolling stats helper function'''
def align_stats_home(home_id, away_id, home_stat, away_stat, team_id):
    
    if home_id == team_id:
        return home_stat
        
    elif away_id == team_id:
        return away_stat
    
    return

''' Gets rolling averages of advanced game statistics'''
def get_rolling_averages_corsi_fenwick(df, team_ids, window):
    
    window_str = str(window)
    
    advanced_corsi = pd.DataFrame(columns=['corsi_for_avg'+ window_str, 'corsi_against_avg'+ window_str, 'fenwick_for_avg'+ window_str, 
                                           'fenwick_against_avg'+ window_str, 'corsi_for_pct_avg'+ window_str, 
                                           'corsi_against_pct_avg'+ window_str, 'fenwick_for_pct_avg'+ window_str, 
                                           'fenwick_against_pct_avg'+ window_str, 'game_id', 'team_id'])
    
    for team_id in team_ids:
    
        home_games = df.loc[(df['home_team_id']==team_id)]
        away_games = df.loc[(df['away_team_id']==team_id)]

        all_games = home_games.append(away_games)

        all_games['team_id'] = team_id

        all_games['corsi_f'] = all_games.apply(lambda x: align_stats_home(x.home_team_id, x.away_team_id, x.corsi_for, x.corsi_against, x.team_id), axis=1)
        all_games['corsi_a'] = all_games.apply(lambda x: align_stats_away(x.home_team_id, x.away_team_id, x.corsi_for, x.corsi_against, x.team_id), axis=1)
        all_games['fenwick_f'] = all_games.apply(lambda x: align_stats_home(x.home_team_id, x.away_team_id, x.fenwick_for, x.fenwick_against, x.team_id), axis=1)
        all_games['fenwick_a'] = all_games.apply(lambda x: align_stats_away(x.home_team_id, x.away_team_id, x.fenwick_for, x.fenwick_against, x.team_id), axis=1)    
        all_games['corsi_f_pct'] = all_games.apply(lambda x: align_stats_home(x.home_team_id, x.away_team_id, x.cf_pct, x.ca_pct, x.team_id), axis=1)
        all_games['corsi_a_pct'] = all_games.apply(lambda x: align_stats_away(x.home_team_id, x.away_team_id, x.cf_pct, x.ca_pct, x.team_id), axis=1)
        all_games['fenwick_f_pct'] = all_games.apply(lambda x: align_stats_home(x.home_team_id, x.away_team_id, x.ff_pct, x.fa_pct, x.team_id), axis=1)
        all_games['fenwick_a_pct'] = all_games.apply(lambda x: align_stats_away(x.home_team_id, x.away_team_id, x.ff_pct, x.fa_pct, x.team_id), axis=1)        

        all_games = all_games.sort_values(by='date_time')

        all_games['corsi_for_avg' + window_str] = all_games.corsi_f.rolling(window, min_periods=1).mean()
        all_games['corsi_against_avg' + window_str] = all_games.corsi_a.rolling(window, min_periods=1).mean()
        all_games['fenwick_for_avg' + window_str] = all_games.fenwick_f.rolling(window, min_periods=1).mean()
        all_games['fenwick_against_avg' + window_str] = all_games.fenwick_a.rolling(window, min_periods=1).mean()
        all_games['corsi_for_pct_avg' + window_str] = all_games.corsi_f_pct.rolling(window, min_periods=1).mean()
        all_games['corsi_against_pct_avg' + window_str] = all_games.corsi_a_pct.rolling(window, min_periods=1).mean()
        all_games['fenwick_for_pct_avg' + window_str] = all_games.fenwick_f_pct.rolling(window, min_periods=1).mean()
        all_games['fenwick_against_pct_avg' + window_str] = all_games.fenwick_a_pct.rolling(window, min_periods=1).mean()

        all_games[['corsi_for_avg'+ window_str, 'corsi_against_avg'+ window_str, 'fenwick_for_avg'+ window_str, 'fenwick_against_avg'+ window_str, 'corsi_for_pct_avg'+ window_str, 
                  'corsi_against_pct_avg'+ window_str, 'fenwick_for_pct_avg'+ window_str, 'fenwick_against_pct_avg'+ window_str]] = all_games[['corsi_for_avg'+ window_str, 'corsi_against_avg'+ window_str, 'fenwick_for_avg'+ window_str, 'fenwick_against_avg'+ window_str, 'corsi_for_pct_avg'+ window_str, 
                  'corsi_against_pct_avg'+ window_str, 'fenwick_for_pct_avg'+ window_str, 'fenwick_against_pct_avg'+ window_str]].shift(periods=1, axis=0)
        
        all_games = all_games[['corsi_for_avg'+ window_str, 'corsi_against_avg'+ window_str, 'fenwick_for_avg'+ window_str, 'fenwick_against_avg'+ window_str, 'corsi_for_pct_avg'+ window_str, 
                  'corsi_against_pct_avg'+ window_str, 'fenwick_for_pct_avg'+ window_str, 'fenwick_against_pct_avg'+ window_str, 'game_id','team_id']]
    
        advanced_corsi = advanced_corsi.append(all_games)
        
    advanced_corsi = rename_corsi_fenwick(advanced_corsi, df, window)

    return advanced_corsi

''' Renames columns for the corsi/fenwick stats'''
def rename_corsi_fenwick(advanced, merged_df, window):

    if window == 10:

        merged_df = merged_df.merge(advanced, left_on=['home_team_id', 'game_id'], right_on=['team_id', 'game_id'], how='left')

        merged_df = merged_df.rename(columns={'corsi_for_avg10':'home_corsi_for_avg_10','corsi_against_avg10':'home_corsi_against_avg_10','fenwick_for_avg10':'home_fenwick_for_avg_10','fenwick_against_avg10':'home_fenwick_against_avg_10','corsi_for_pct_avg10':'home_corsi_for_pct_avg_10','corsi_against_pct_avg10':'home_corsi_against_pct_avg_10', 'fenwick_for_pct_avg10':'home_fenwick_for_pct_avg_10','fenwick_against_pct_avg10':'home_fenwick_against_pct_avg_10'})

        merged_df = merged_df.merge(advanced, left_on=['away_team_id', 'game_id'], right_on=['team_id', 'game_id'], how='left')

        merged_df = merged_df.rename(columns={'corsi_for_avg10':'away_corsi_for_avg_10','corsi_against_avg10':'away_corsi_against_avg_10','fenwick_for_avg10':'away_fenwick_for_avg_10','fenwick_against_avg10':'away_fenwick_against_avg_10','corsi_for_pct_avg10':'away_corsi_for_pct_avg_10','corsi_against_pct_avg10':'away_corsi_against_pct_avg_10', 'fenwick_for_pct_avg10':'away_fenwick_for_pct_avg_10','fenwick_against_pct_avg10':'away_fenwick_against_pct_avg_10'})

    if window == 3:

        merged_df = merged_df.merge(advanced, left_on=['home_team_id', 'game_id'], right_on=['team_id', 'game_id'], how='left')

        merged_df = merged_df.rename(columns={'corsi_for_avg3':'home_corsi_for_avg_3','corsi_against_avg3':'home_corsi_against_avg_3','fenwick_for_avg3':'home_fenwick_for_avg_3','fenwick_against_avg3':'home_fenwick_against_avg_3','corsi_for_pct_avg3':'home_corsi_for_pct_avg_3','corsi_against_pct_avg3':'home_corsi_against_pct_avg_3', 'fenwick_for_pct_avg3':'home_fenwick_for_pct_avg_3','fenwick_against_pct_avg3':'home_fenwick_against_pct_avg_3'})

        merged_df = merged_df.merge(advanced, left_on=['away_team_id', 'game_id'], right_on=['team_id', 'game_id'], how='left')

        merged_df = merged_df.rename(columns={'corsi_for_avg3':'away_corsi_for_avg_3','corsi_against_avg3':'away_corsi_against_avg_3','fenwick_for_avg3':'away_fenwick_for_avg_3','fenwick_against_avg3':'away_fenwick_against_avg_3','corsi_for_pct_avg3':'away_corsi_for_pct_avg_3','corsi_against_pct_avg3':'away_corsi_against_pct_avg_3', 'fenwick_for_pct_avg3':'away_fenwick_for_pct_avg_3','fenwick_against_pct_avg3':'away_fenwick_against_pct_avg_3'})

    if window == 40:

        merged_df = merged_df.merge(advanced, left_on=['home_team_id', 'game_id'], right_on=['team_id', 'game_id'], how='left')

        merged_df = merged_df.rename(columns={'corsi_for_avg40':'home_corsi_for_avg_40','corsi_against_avg40':'home_corsi_against_avg_40','fenwick_for_avg40':'home_fenwick_for_avg_40','fenwick_against_avg40':'home_fenwick_against_avg_40','corsi_for_pct_avg40':'home_corsi_for_pct_avg_40','corsi_against_pct_avg40':'home_corsi_against_pct_avg_40', 'fenwick_for_pct_avg40':'home_fenwick_for_pct_avg_40','fenwick_against_pct_avg40':'home_fenwick_against_pct_avg_40'})

        merged_df = merged_df.merge(advanced, left_on=['away_team_id', 'game_id'], right_on=['team_id', 'game_id'], how='left')

        merged_df = merged_df.rename(columns={'corsi_for_avg40':'away_corsi_for_avg_40','corsi_against_avg40':'away_corsi_against_avg_40','fenwick_for_avg40':'away_fenwick_for_avg_40','fenwick_against_avg40':'away_fenwick_against_avg_40','corsi_for_pct_avg40':'away_corsi_for_pct_avg_40','corsi_against_pct_avg40':'away_corsi_against_pct_avg_40', 'fenwick_for_pct_avg40':'away_fenwick_for_pct_avg_40','fenwick_against_pct_avg40':'away_fenwick_against_pct_avg_40'})
    
    return merged_df


''' Helper function for calculating win percentage'''
def get_win_helper_home(target):
    if target == 0:
        return 1
    else:
        return 0

''' Helper function for calculating win percentage'''
def get_win_helper_away(target):
    if target == 1:
        return 1
    else:
        return 0

''' Gets win pct for each team for last n games'''
def get_win_pct(df, team_ids, window):
    
    window_str = str(window)
    
    win_pcts = pd.DataFrame(columns=['win_pct'+window_str, 'game_id', 'team_id'])
    
    for team_id in team_ids:

        home_games = df.loc[(df['home_team_id']==team_id)]
        away_games = df.loc[(df['away_team_id']==team_id)]

        home_games['win_loss'] = home_games['target'].apply(lambda x: get_win_helper_home(x))
        away_games['win_loss'] = away_games['target'].apply(lambda x: get_win_helper_away(x))

        all_games = home_games.append(away_games)
        all_games = all_games.sort_values(by='date_time')

        all_games['win_pct'+window_str] = all_games.win_loss.rolling(window, min_periods=1).mean()   
        all_games[['win_pct'+window_str]] = all_games[['win_pct'+window_str]].shift(periods=1, axis=0)

        all_games['team_id'] = team_id
        all_games = all_games[['win_pct'+window_str, 'game_id', 'team_id']]
        
        #print(team_id)
        #print(win_pcts.columns)
        win_pcts = win_pcts.append(all_games)
        
    win_pcts = rename_win_pct(win_pcts, df, window)
    
    return win_pcts

'''Rename columns'''
def rename_win_pct(win_pcts, main_df, window):

    if window == 10:

        merged_df = main_df.merge(win_pcts, left_on=['game_id', 'home_team_id'], right_on=['game_id','team_id'], how='inner')

        merged_df = merged_df.rename(columns={'win_pct10':'home_win_pct_10'})

        merged_df = merged_df.merge(win_pcts, left_on=['game_id', 'away_team_id'], right_on=['game_id', 'team_id'], how='inner')

        merged_df = merged_df.rename(columns={'win_pct10':'away_win_pct_10'})

    elif window == 40:

        merged_df = main_df.merge(win_pcts, left_on=['game_id', 'home_team_id'], right_on=['game_id','team_id'], how='inner')

        merged_df = merged_df.rename(columns={'win_pct40':'home_win_pct_40'})

        merged_df = merged_df.merge(win_pcts, left_on=['game_id', 'away_team_id'], right_on=['game_id', 'team_id'], how='inner')

        merged_df = merged_df.rename(columns={'win_pct40':'away_win_pct_40'})

    elif window == 82:

        merged_df = main_df.merge(win_pcts, left_on=['game_id', 'home_team_id'], right_on=['game_id','team_id'], how='inner')

        merged_df = merged_df.rename(columns={'win_pct82':'home_win_pct_82'})

        merged_df = merged_df.merge(win_pcts, left_on=['game_id', 'away_team_id'], right_on=['game_id', 'team_id'], how='inner')

        merged_df = merged_df.rename(columns={'win_pct82':'away_win_pct_82'})

    return merged_df

''' Computes rolling averages for basic game stats'''
def get_avg_stats(df, team_ids, window):
    
    window_str = str(window)
    
    stats = pd.DataFrame(columns=['goals_for'+ window_str, 'goals_against'+ window_str, 'hits'+ window_str, 'pim'+ window_str, 'ppg'+ window_str, 'face_off_pct'+ window_str, 'giveaways'+ window_str, 'takeaways'+ window_str, 'game_id', 'team_id'])
    
    for team_id in team_ids:

        home_games = df.loc[(df['home_team_id']==team_id)]
        away_games = df.loc[(df['away_team_id']==team_id)]

        all_games = home_games.append(away_games)

        all_games['team_id'] = team_id
        
        all_games['goals_for'] = all_games.apply(lambda x: align_stats_home(x.home_team_id, x.away_team_id, x.home_goals, x.away_goals, x.team_id), axis=1)
        all_games['goals_against'] = all_games.apply(lambda x: align_stats_away(x.home_team_id, x.away_team_id, x.home_goals, x.away_goals, x.team_id), axis=1)
        all_games['hits'] = all_games.apply(lambda x: align_stats_home(x.home_team_id, x.away_team_id, x.home_hits, x.away_hits, x.team_id), axis=1)
        all_games['pim'] = all_games.apply(lambda x: align_stats_home(x.home_team_id, x.away_team_id, x.home_pim, x.away_pim, x.team_id), axis=1)    
        all_games['ppg'] = all_games.apply(lambda x: align_stats_home(x.home_team_id, x.away_team_id, x.home_PPG, x.away_PPG, x.team_id), axis=1)
        all_games['face_off_pct'] = all_games.apply(lambda x: align_stats_home(x.home_team_id, x.away_team_id, x.home_faceoff_win_pct, x.away_faceoff_win_pct, x.team_id), axis=1)
        all_games['giveaways'] = all_games.apply(lambda x: align_stats_home(x.home_team_id, x.away_team_id, x.home_giveaways, x.away_giveaways, x.team_id), axis=1)
        all_games['takeaways'] = all_games.apply(lambda x: align_stats_home(x.home_team_id, x.away_team_id, x.home_takeaways, x.away_takeaways, x.team_id), axis=1)        
 
        all_games = all_games.sort_values(by='date_time')
    
        all_games['goals_for' + window_str] = all_games.goals_for.rolling(window, min_periods=1).mean()
        all_games['goals_against' + window_str] = all_games.goals_against.rolling(window, min_periods=1).mean()
        all_games['hits' + window_str] = all_games.hits.rolling(window, min_periods=1).mean()
        all_games['pim' + window_str] = all_games.pim.rolling(window, min_periods=1).mean()
        all_games['ppg' + window_str] = all_games.ppg.rolling(window, min_periods=1).mean()
        all_games['face_off_pct' + window_str] = all_games.face_off_pct.rolling(window, min_periods=1).mean()
        all_games['giveaways' + window_str] = all_games.giveaways.rolling(window, min_periods=1).mean()
        all_games['takeaways' + window_str] = all_games.takeaways.rolling(window, min_periods=1).mean()
        
        all_games[['goals_for'+ window_str, 'goals_against'+ window_str, 'hits'+ window_str, 'pim'+ window_str, 'ppg'+ window_str, 'face_off_pct'+ window_str, 'giveaways'+ window_str, 'takeaways'+ window_str]] = all_games[['goals_for'+ window_str, 'goals_against'+ window_str, 'hits'+ window_str, 'pim'+ window_str, 'ppg'+ window_str, 'face_off_pct'+ window_str, 'giveaways'+ window_str, 'takeaways'+ window_str]].shift(periods=1, axis=0)
        
        all_games = all_games[['goals_for'+ window_str, 'goals_against'+ window_str, 'hits'+ window_str, 'pim'+ window_str, 'ppg'+ window_str, 'face_off_pct'+ window_str, 'giveaways'+ window_str, 'takeaways'+ window_str, 'game_id', 'team_id']]
        
        stats = stats.append(all_games)
        
    stats = rename_stats(stats, df, window)

    return stats

'''Rename columns'''
def rename_stats(stats, merged_df, window):

    if window == 5:
        merged_df = merged_df.merge(stats, left_on=['home_team_id', 'game_id'], right_on=['team_id', 'game_id'], how='left')

        merged_df = merged_df.rename(columns={'goals_for5':'home_goals_for_5','goals_against5':'home_goals_against_5','hits5':'home_hits_5', 'pim5':'home_pim_5','ppg5':'home_ppg_5','face_off_pct5':'home_face_off_pct_5','giveaways5':'home_giveaways_5', 'takeaways5':'home_takeaways_5'})

        merged_df = merged_df.merge(stats, left_on=['away_team_id', 'game_id'], right_on=['team_id', 'game_id'], how='left')

        merged_df = merged_df.rename(columns={'goals_for5':'away_goals_for_5','goals_against5':'away_goals_against_5','hits5':'away_hits_5', 'pim5':'away_pim_5','ppg5':'away_ppg_5','face_off_pct5':'away_face_off_pct_5','giveaways5':'away_giveaways_5', 'takeaways5':'away_takeaways_5'})

    elif window == 40:

        merged_df = merged_df.merge(stats, left_on=['home_team_id', 'game_id'], right_on=['team_id', 'game_id'], how='left')

        merged_df = merged_df.rename(columns={'goals_for40':'home_goals_for_40','goals_against40':'home_goals_against_40','hits40':'home_hits_40', 'pim40':'home_pim_40','ppg40':'home_ppg_40','face_off_pct40':'home_face_off_pct_40','giveaways40':'home_giveaways_40', 'takeaways40':'home_takeaways_40'})

        merged_df = merged_df.merge(stats, left_on=['away_team_id', 'game_id'], right_on=['team_id', 'game_id'], how='left')

        merged_df = merged_df.rename(columns={'goals_for40':'away_goals_for_40','goals_against40':'away_goals_against_40','hits40':'away_hits_40', 'pim40':'away_pim_40','ppg40':'away_ppg_40','face_off_pct40':'away_face_off_pct_40','giveaways40':'away_giveaways_40', 'takeaways40':'away_takeaways_40'})

    elif window == 82:

        merged_df = merged_df.merge(stats, left_on=['home_team_id', 'game_id'], right_on=['team_id', 'game_id'], how='left')

        merged_df = merged_df.rename(columns={'goals_for82':'home_goals_for_82','goals_against82':'home_goals_against_82','hits82':'home_hits_82', 'pim82':'home_pim_82','ppg82':'home_ppg_82','face_off_pct82':'home_face_off_pct_82','giveaways82':'home_giveaways_82', 'takeaways82':'home_takeaways_82'})

        merged_df = merged_df.merge(stats, left_on=['away_team_id', 'game_id'], right_on=['team_id', 'game_id'], how='left')

        merged_df = merged_df.rename(columns={'goals_for82':'away_goals_for_82','goals_against82':'away_goals_against_82','hits82':'away_hits_82', 'pim82':'away_pim_82','ppg82':'away_ppg_82','face_off_pct82':'away_face_off_pct_82','giveaways82':'away_giveaways_82', 'takeaways82':'away_takeaways_82'})

    return merged_df

'''Get basic stats differentials'''
def get_stats_differentials(merged_df):

    merged_df['goals_for_5_avg'] =  merged_df['away_goals_for_5'] - merged_df['home_goals_for_5']
    merged_df['goals_against_5_avg'] =  merged_df['away_goals_against_5'] - merged_df['home_goals_against_5']
    merged_df['hits_5_avg'] =  merged_df['away_hits_5'] - merged_df['home_hits_5']
    merged_df['pim_5_avg'] =  merged_df['away_pim_5'] - merged_df['home_pim_5']
    merged_df['ppg_5_avg'] =  merged_df['away_ppg_5'] - merged_df['home_ppg_5']
    merged_df['face_off_pct_5_avg'] =  merged_df['away_face_off_pct_5'] - merged_df['home_face_off_pct_5']
    merged_df['giveaways_5_avg'] =  merged_df['away_giveaways_5'] - merged_df['home_giveaways_5']
    merged_df['takeaways_5_avg'] =  merged_df['away_takeaways_5'] - merged_df['home_takeaways_5']

    merged_df['goals_for_40_avg'] =  merged_df['away_goals_for_40'] - merged_df['home_goals_for_40']
    merged_df['goals_against_40_avg'] =  merged_df['away_goals_against_40'] - merged_df['home_goals_against_40']
    merged_df['hits_40_avg'] =  merged_df['away_hits_40'] - merged_df['home_hits_40']
    merged_df['pim_40_avg'] =  merged_df['away_pim_40'] - merged_df['home_pim_40']
    merged_df['ppg_40_avg'] =  merged_df['away_ppg_40'] - merged_df['home_ppg_40']
    merged_df['face_off_pct_40_avg'] =  merged_df['away_face_off_pct_40'] - merged_df['home_face_off_pct_40']
    merged_df['giveaways_40_avg'] =  merged_df['away_giveaways_40'] - merged_df['home_giveaways_40']
    merged_df['takeaways_40_avg'] =  merged_df['away_takeaways_40'] - merged_df['home_takeaways_40']

    merged_df['goals_for_82_avg'] =  merged_df['away_goals_for_82'] - merged_df['home_goals_for_82']
    merged_df['goals_against_82_avg'] =  merged_df['away_goals_against_82'] - merged_df['home_goals_against_82']
    merged_df['hits_82_avg'] =  merged_df['away_hits_82'] - merged_df['home_hits_82']
    merged_df['pim_82_avg'] =  merged_df['away_pim_82'] - merged_df['home_pim_82']
    merged_df['ppg_82_avg'] =  merged_df['away_ppg_82'] - merged_df['home_ppg_82']
    merged_df['face_off_pct_82_avg'] =  merged_df['away_face_off_pct_82'] - merged_df['home_face_off_pct_82']
    merged_df['giveaways_82_avg'] =  merged_df['away_giveaways_82'] - merged_df['home_giveaways_82']
    merged_df['takeaways_82_avg'] =  merged_df['away_takeaways_82'] - merged_df['home_takeaways_82']

    return merged_df

'''Get win differentials'''
def get_win_differentials(merged_df):

    merged_df['win_pct_82'] =  merged_df['away_win_pct_82'] - merged_df['home_win_pct_82']
    merged_df['win_pct_40'] =  merged_df['away_win_pct_40'] - merged_df['home_win_pct_40']
    merged_df['win_pct_10'] =  merged_df['away_win_pct_10'] - merged_df['home_win_pct_10']  

    return merged_df

'''Get corsi_differentials'''
def get_corsi_differentials(merged_df):

    merged_df['corsi_against_avg_10'] =  merged_df['away_corsi_against_avg_10'] - merged_df['home_corsi_against_avg_10']
    merged_df['fenwick_for_avg_10'] =  merged_df['away_fenwick_for_avg_10'] - merged_df['home_fenwick_for_avg_10']
    merged_df['fenwick_against_avg_10'] =  merged_df['away_fenwick_against_avg_10'] - merged_df['home_fenwick_against_avg_10']
    merged_df['corsi_for_pct_avg_10'] =  merged_df['away_corsi_for_pct_avg_10'] - merged_df['home_corsi_for_pct_avg_10']
    merged_df['corsi_against_pct_avg_10'] =  merged_df['away_corsi_against_pct_avg_10'] - merged_df['home_corsi_against_pct_avg_10']
    merged_df['fenwick_for_pct_avg_10'] =  merged_df['away_fenwick_for_pct_avg_10'] - merged_df['home_fenwick_for_pct_avg_10']
    merged_df['fenwick_against_pct_avg_10'] =  merged_df['away_fenwick_against_pct_avg_10'] - merged_df['home_fenwick_against_pct_avg_10']
    merged_df['corsi_for_avg_10'] =  merged_df['away_corsi_for_avg_10'] - merged_df['home_corsi_for_avg_10']

    merged_df['corsi_against_avg_3'] =  merged_df['away_corsi_against_avg_3'] - merged_df['home_corsi_against_avg_3']
    merged_df['fenwick_for_avg_3'] =  merged_df['away_fenwick_for_avg_3'] - merged_df['home_fenwick_for_avg_3']
    merged_df['fenwick_against_avg_3'] =  merged_df['away_fenwick_against_avg_3'] - merged_df['home_fenwick_against_avg_3']
    merged_df['corsi_for_pct_avg_3'] =  merged_df['away_corsi_for_pct_avg_3'] - merged_df['home_corsi_for_pct_avg_3']
    merged_df['corsi_against_pct_avg_3'] =  merged_df['away_corsi_against_pct_avg_3'] - merged_df['home_corsi_against_pct_avg_3']
    merged_df['fenwick_for_pct_avg_3'] =  merged_df['away_fenwick_for_pct_avg_3'] - merged_df['home_fenwick_for_pct_avg_3']
    merged_df['fenwick_against_pct_avg_3'] =  merged_df['away_fenwick_against_pct_avg_3'] - merged_df['home_fenwick_against_pct_avg_3']
    merged_df['corsi_for_avg_3'] =  merged_df['away_corsi_for_avg_3'] - merged_df['home_corsi_for_avg_3']

    merged_df['corsi_against_avg_40'] =  merged_df['away_corsi_against_avg_40'] - merged_df['home_corsi_against_avg_40']
    merged_df['fenwick_for_avg_40'] =  merged_df['away_fenwick_for_avg_40'] - merged_df['home_fenwick_for_avg_40']
    merged_df['fenwick_against_avg_40'] =  merged_df['away_fenwick_against_avg_40'] - merged_df['home_fenwick_against_avg_40']
    merged_df['corsi_for_pct_avg_40'] =  merged_df['away_corsi_for_pct_avg_40'] - merged_df['home_corsi_for_pct_avg_40']
    merged_df['corsi_against_pct_avg_40'] =  merged_df['away_corsi_against_pct_avg_40'] - merged_df['home_corsi_against_pct_avg_40']
    merged_df['fenwick_for_pct_avg_40'] =  merged_df['away_fenwick_for_pct_avg_40'] - merged_df['home_fenwick_for_pct_avg_40']
    merged_df['fenwick_against_pct_avg_40'] =  merged_df['away_fenwick_against_pct_avg_40'] - merged_df['home_fenwick_against_pct_avg_40']
    merged_df['corsi_for_avg_40'] =  merged_df['away_corsi_for_avg_40'] - merged_df['home_corsi_for_avg_40']

    return merged_df

''' Get columns needed for following steps'''
def select_preprocessing_columns(merged_df):
    return merged_df[['game_id',
        'away_team_id',
        'home_team_id',
        'date_time_GMT_x',
        'venue_time_zone_offset',
        'target',
        'away_starting_goalie',
        'home_starting_goalie',
        'shots_5_avg',
        'saves_5_avg',
        'pps_5_avg',
        'shs_5_avg',
        'evenSaves_5_avg',
        'save%_5_avg',
        'ppsave%_5_avg',
        'evenSave%_5_avg',
        'shots_10_avg',
        'saves_10_avg',
        'pps_10_avg',
        'shs_10_avg',
        'evenSaves_10_avg',
        'save%_10_avg',
        'ppsave%_10_avg',
        'evenSave%_10_avg',
        'shots_40_avg',
        'saves_40_avg',
        'pps_40_avg',
        'shs_40_avg',
        'evenSaves_40_avg',
        'save%_40_avg',
        'ppsave%_40_avg',
        'evenSave%_40_avg',
        'head_2_head_home_p10',
        'head_2_head_home_p5',
        'head_2_head_home_p2',
        'win_pct_82',
        'win_pct_40',
        'win_pct_10',
        'corsi_against_avg_10',
        'fenwick_for_avg_10',
        'fenwick_against_avg_10',
        'corsi_for_pct_avg_10',
        'corsi_against_pct_avg_10',
        'fenwick_for_pct_avg_10',
        'fenwick_against_pct_avg_10',
        'corsi_for_avg_10',
        'corsi_against_avg_3',
        'fenwick_for_avg_3',
        'fenwick_against_avg_3',
        'corsi_for_pct_avg_3',
        'corsi_against_pct_avg_3',
        'fenwick_for_pct_avg_3',
        'fenwick_against_pct_avg_3',
        'corsi_for_avg_3',
        'corsi_against_avg_40',
        'fenwick_for_avg_40',
        'fenwick_against_avg_40',
        'corsi_for_pct_avg_40',
        'corsi_against_pct_avg_40',
        'fenwick_for_pct_avg_40',
        'fenwick_against_pct_avg_40',
        'corsi_for_avg_40',
        'goals_for_5_avg',
        'goals_against_5_avg',
        'hits_5_avg',
        'pim_5_avg',
        'ppg_5_avg',
        'face_off_pct_5_avg',
        'giveaways_5_avg',
        'takeaways_5_avg',
        'goals_for_40_avg',
        'goals_against_40_avg',
        'hits_40_avg',
        'pim_40_avg',
        'ppg_40_avg',
        'face_off_pct_40_avg',
        'giveaways_40_avg',
        'takeaways_40_avg',
        'goals_for_82_avg',
        'goals_against_82_avg',
        'hits_82_avg',
        'pim_82_avg',
        'ppg_82_avg',
        'face_off_pct_82_avg',
        'giveaways_82_avg',
        'takeaways_82_avg']]

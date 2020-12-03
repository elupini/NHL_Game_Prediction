''' Takes predictions and probabilites and joins them with team info and game details, outputs to .csv'''
def process_predictions(y_pred, proba, df, team_info):

    home_prob = []
    away_prob = []
    for i in range(len(proba)):
        home_prob.append(proba[i][0])
        away_prob.append(proba[i][1])

    predictions = df.iloc[round(0.75 * len(df)):]
    predictions['pred'] = y_pred
    predictions['home_prob'] = home_prob
    predictions['away_prob'] = away_prob
    team_info_reduced = team_info[['team_id','shortName']]
    predictions = predictions.merge(team_info_reduced, left_on='away_team_id', right_on='team_id', how='left')
    predictions = predictions.rename(columns={'shortName':'away_team'})
    predictions = predictions.merge(team_info_reduced, left_on='home_team_id', right_on='team_id', how='left')
    predictions = predictions.rename(columns={'shortName':'home_team'})

    predictions = predictions[['date_time_GMT_x','home_team','away_team','home_prob','away_prob','pred','target']]
    
    predictions = predictions.rename(columns={'date_time_GMT_x':'date_time_GMT'})

    return predictions

'''Gets relevant columns for modelling'''
def get_modelling_columns(nhl_df):
    return nhl_df[[
        'venue_time_zone_offset',
        'target',
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
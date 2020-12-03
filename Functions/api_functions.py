'''Extracts the data from the json content. Outputs results in a dataframe'''
def get_play_df(content):
    events = {}
    event_num = 0
    
    home = content['gameData']['teams']['home']['id']
    away = content['gameData']['teams']['away']['id']
    
    for i in range(len(content['liveData']['plays']['allPlays'])):
        temp = {}
        if content['liveData']['plays']['allPlays'][i]['result']['event'] == 'Penalty':
            temp['event_type'] = 'Penalty'
            temp['penalty_minutes'] = content['liveData']['plays']['allPlays'][i]['result']['penaltyMinutes']
            temp['time_of_event'] = content['liveData']['plays']['allPlays'][i]['about']['periodTime']
            temp['period'] = content['liveData']['plays']['allPlays'][i]['about']['ordinalNum']
            temp['current_score'] = content['liveData']['plays']['allPlays'][i]['about']['goals']

            if content['liveData']['plays']['allPlays'][i]['team']['id'] == home:
                temp['team'] = 'home'
            elif content['liveData']['plays']['allPlays'][i]['team']['id'] == away:
                temp['team'] = 'away'
            else:
                temp['team'] = 'error'

            events[event_num] = temp
            event_num += 1

        if content['liveData']['plays']['allPlays'][i]['result']['event'] in ['Blocked Shot', 'Goal', 'Missed Shot', 'Shot']:
            temp['event_type'] = content['liveData']['plays']['allPlays'][i]['result']['event']
            temp['penalty_minutes'] = 0
            temp['time_of_event'] = content['liveData']['plays']['allPlays'][i]['about']['periodTime']
            temp['period'] = content['liveData']['plays']['allPlays'][i]['about']['ordinalNum']
            temp['current_score'] = content['liveData']['plays']['allPlays'][i]['about']['goals']

            if content['liveData']['plays']['allPlays'][i]['team']['id'] == home:
                temp['team'] = 'home'
            elif content['liveData']['plays']['allPlays'][i]['team']['id'] == away:
                temp['team'] = 'away'
            else:
                temp['team'] = 'error'

            events[event_num] = temp
            event_num += 1
        
    events_df = pd.DataFrame(events)  
    events_df_t = events_df.transpose()
    
    return events_df_t

''' Helper function to get time of game events in seconds'''
def get_seconds(time, period):
    
    if period == 'OT':
        
        period = '4th'
    
    elif period == 'SO':
        
        return 3605
    
    seconds = int(time[3:])
    minutes = int(time[0:2])    
    game_period = int(period[0]) -1
    
    timestamp = (20 * 60 * game_period) + (60 * minutes) + seconds
    
    return timestamp

''' Main function that determines shots, and if there are any active penalties (which would negate
the shot being counted towards the advanced stats). The function returns the shot counts for each team'''
def count_all_shots(events_df_t):
    home_shots = 0
    away_shots = 0
    home_blocked_shots = 0
    away_blocked_shots = 0
    active_penalty = False
    home_penalty = False
    away_penalty = False
    two_man_advtg = False
    four_v_four = False
    major_penalty = False
    shot_types = ['Blocked Shot', 'Goal', 'Missed Shot', 'Shot']
    
    for i in range(len(events_df_t)):
        
        event = events_df_t['event_type'][i]
        event_time = events_df_t['timestamp'][i]
        
        if events_df_t['period'][i] == 'SO':
            
            return home_shots, away_shots, home_blocked_shots, away_blocked_shots
        
        if major_penalty == True:
            
            if end_penalty_time <= event_time:
            
                major_penalty = False
        
        if active_penalty == True:
            
            if (event in shot_types) & (end_penalty_time <= event_time):
                
                active_penalty = False
                four_v_four = False
            
            elif event == 'Penalty':
                
                if ((events_df_t['team'][i] == 'home') & (home_penalty == True) or ((events_df_t['team'][i] == 'away') & (away_penalty == True))):
                    
                    added_time = 60 * events_df_t['penalty_minutes'][i]
                    end_penalty_time = event_time + added_time
                    two_man_advtg = True
                    
                else:
                    
                    # Currently does not take into account 4v4 as even strength, will fix later
                    
                    added_time = 60 * events_df_t['penalty_minutes'][i]
                    end_penalty_time = event_time + added_time
                    four_v_four = True
        
        if (event in shot_types) & (active_penalty == False):
            
            if events_df_t['team'][i] == 'home':
                
                if event == 'Blocked Shot':
                    
                    home_blocked_shots += 1
                    
                else:
                    
                    home_shots += 1
                
            else:
                
                if event == 'Blocked Shot':
                    
                    away_blocked_shots += 1
                    
                else:
                
                    away_shots += 1
                    
        elif (event == 'Penalty') & (active_penalty == False):
            
            active_penalty = True
            
            if events_df_t['penalty_minutes'][i] >= 5:
                
                major_penalty = True
            
            if events_df_t['team'][i] == 'home':
                
                home_penalty = True
                
            else:
                
                away_penalty = True
                
            added_time = 60 * events_df_t['penalty_minutes'][i]
            end_penalty_time = event_time + added_time
        
        elif (event == 'Goal') & (active_penalty == True) & (major_penalty == False):
            
            if two_man_advtg == True:
                
                two_man_advtg = False
            
            elif four_v_four == True:
                
                if events_df_t['team'][i] == 'home':
                    
                    away_penalty = False
                
                elif events_df_t['team'][i] == 'away':
                    
                    home_penalty = False
                
                four_v_four = False
                
            else:
                
                active_penalty = False
                home_penalty = False
                away_penalty = False
    
    return home_shots, away_shots, home_blocked_shots, away_blocked_shots

'''Based on the output of the above function, this calculates that actual advanced Corsi and Fenwick stats'''
def calc_advanced_stats(home_shots, away_shots, home_blocked_shots, away_blocked_shots):
    corsi_for = home_shots + home_blocked_shots
    corsi_against = away_shots + away_blocked_shots
    cf_pct = corsi_for/(corsi_for + corsi_against)
    ca_pct = corsi_against/(corsi_for + corsi_against)
    fenwick_for = home_shots
    fenwick_against = away_shots
    ff_pct = home_shots/(home_shots + away_shots)
    fa_pct = away_shots/(home_shots + away_shots)
    return corsi_for, corsi_against, cf_pct, ca_pct, fenwick_for, fenwick_against, ff_pct, fa_pct

'''Performs the API call to the NHL API'''
def get_api_data(game_id):
    # Call API
    URL = f"https://statsapi.web.nhl.com/api/v1/game/{game_id}/feed/live"
    # sending get request and saving the response as response object 
    r = re.get(url=URL)
    content = r.json()
    return content

'''Main function to call API. Uses game IDs in the Kaggle dataset to perform the call'''
def get_game_data(game_list):
    
    game_data_dict = {}
    i = 0
    
    for game_id in tqdm(game_list):
        try:
            
            game_data_dict[game_id] = get_api_data(game_id)
        
        except Exception as e:
            
            print('\n======EXCEPTION=====')
            print(e)
            
            game_data_dict[game_id] = 0
            continue
            
        # Saving checkpoint
        if i % 100 == 0:
            print(f"Completed {i} iterations")
             #filename = f'game_data_checkpoint_{i}.sav'
             #pickle.dump(game_data_dict, open(filename, 'wb'))        
        i+=1
    return game_data_dict
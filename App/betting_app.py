import streamlit as st
import pandas as pd
import numpy as np
from svglib.svglib import svg2rlg
from reportlab.graphics import renderPDF, renderPM
from PIL import Image
sys.path.insert(0, '/NHL_Game_Prediction/Functions/')
from functions.app_functions import *

st.set_page_config(
    page_title="Ada",
    layout="wide",
    initial_sidebar_state="expanded")

'''Creates checkboxes'''
def create_checkbox(name, label, i, check):

    if check == False:

        checkbox_dict[name] = right_column.checkbox(label, value=check)

    else:

        if i % 2 == 0:
            checkbox_dict[name] = left_column.checkbox(label, value=check)
        else:
            checkbox_dict[name] = left_middle.checkbox(label, value=check)

    return checkbox_dict[name]

# Set filepath's for data
st.title('NHL Betting Predictions and Suggestions')
filepath_pred = 'app_pred.csv'

#@st.cache
def load_data(filepath):
    data = pd.read_csv(filepath)

    return data

# Read in data
data_load_state = st.text('Loading data...')
data = load_data(filepath_pred)
data_load_state.text("Done! (using st.cache)")

# Include raw data for debugging purposes
if st.checkbox('Show raw data'):
    st.subheader('Raw data')
    st.write(data)

games_exist=True

profit_games, bad_games, games_exist = get_positive_profit(data)

bad_games_list = list(bad_games['home_team'])

# Create sidebar 'games of the day'
st.sidebar.markdown(f"### Today's Games - {data.iloc[0]['date_time']}")
st.sidebar.markdown("\n")
for i in range(len(data)):

    st.sidebar.markdown(f"#### {data.iloc[i]['away_team']} @ {data.iloc[i]['home_team']} --- {data.iloc[i]['date_time_GMT'][10:16]} EST")


# Formatting
st.sidebar.write('\n')
st.sidebar.write('\n')
st.sidebar.write('\n')
st.sidebar.markdown('Updates occur daily @ 1am PST')
st.sidebar.write('\n')
st.sidebar.write('\n')
st.sidebar.write('\n')
st.sidebar.markdown('''
---
*Created by [Elliot Lupini](https://www.linkedin.com/in/elliot-lupini-8824681b1/)*
'''
)

step_1 = st.beta_expander(label='Step 1/3 - Game Selection', expanded=True)
with step_1:
        
    # Create format for body of app
    left_column, left_middle, right_middle, right_column, far_right = st.beta_columns(5)

    # Create text classification of models confidence on each game
    data_classified = classify_matchup(data)

    left_column.subheader('Select Games to Consider')

    left_column.write('\n')
    left_column.write('\n')
    left_column.write('\n')
    left_middle.subheader('\n')
    left_middle.subheader('\n')
    left_middle.subheader('\n')
    left_middle.subheader('\n')


    # Generate game selection grid

    checkbox_dict = {}
    warning = False

    for i in range(len(data)):

        check = True

        if data.iloc[i]['home_team'] in bad_games_list:
            if warning == False:
                right_column.warning('Betting Disabled - Profit/Risk Margins Too Small')

            check = False
            right_column.markdown(f"{data.iloc[i]['home_team']} vs. {data.iloc[i]['away_team']}")
            
            warning = True

        elif i % 2 == 0:
            create_checkbox(f'checkbox_{i}',f"{data.iloc[i]['home_team']} vs. {data.iloc[i]['away_team']}", i, check)
            left_column.markdown(f"*{data_classified.iloc[i]['text_prediction']}*")
            left_column.markdown("---")
        else:
            create_checkbox(f'checkbox_{i}',f"{data.iloc[i]['home_team']} vs. {data.iloc[i]['away_team']}", i, check)
            left_middle.markdown(f"*{data_classified.iloc[i]['text_prediction']}*")
            left_middle.markdown("---")


step_2 = st.beta_expander(label='Step 2/3 - Wager', expanded=True)
with step_2:

    left_column, right_column = st.beta_columns(2)
    # Wager numeric input
    left_column.markdown('### Wager')
    betting_amount = left_column.number_input('', min_value=1, format='%.2f')

# Holds indexes of games selected by user
game_list = []

# Extract indexes of games selected by user
for key, value in checkbox_dict.items():

    if value:
        
        game_list.append(extract_num(key))

step_3 = st.beta_expander(label='Step 3/3 - Risk', expanded=True)
with step_3:

    _, left_column, right_column = st.beta_columns([0.0001, 0.48, 0.50])
    risk_slider_length = len(game_list)
    
    # Risk Slider

    left_column.subheader('Select a level of risk')

    if len(game_list) == 0:
        left_column.warning('Please select at least 1 game')
    elif (len(game_list) < 3) & (len(game_list) > 1):
        risk_level = left_column.radio(label='',options=['Lower Risk, Lower Reward','Higher Risk, Higher Reward'])
        if risk_level == 'Lower Risk, Lower Reward':
            risk_level = 1
        else:
            risk_level = 2
    elif (len(game_list) == 1):
        left_column.warning('Only one game selected, no risk options available. Press Submit to place one bet.')
        risk_level=1
    else:
        risk_level = left_column.slider('', min_value=1, max_value=risk_slider_length, value=round(risk_slider_length/2))



    left_column.markdown("---")

# Create button to execute wager calculations
if st.button('Submit'):
    
    # Extract indexes of games selected by user
    game_list = []
    for key, value in checkbox_dict.items():

        if value:
            
            game_list.append(extract_num(key))

    # st.write(game_list)
    # st.write(profit_games)

    if len(game_list) == 0: # Invalid input
        st.markdown(f"Please select at least 1 game")

    elif len(game_list) > len(profit_games):

        st.error('Make sure only valid games are selected')

    else:

        # Call function to calculate wager
        data_load_state = st.text('Calculating...')
        wager = calc_bets(betting_amount, risk_level, profit_games, game_list)
        prob_losing = get_prob_lose(wager)
        data_load_state.text("Done!")

        # Print output to app
        st.markdown(f"Based on our model, you should wager :")
        for i in range(len(wager)):

            st.markdown("${:.2f} on {}".format(round(wager.iloc[i]['wager'], 2), wager.iloc[i]['betting_team']))
            st.markdown("Our confidence of victory is {:.2f}% and your profit would be ${:.2f}".format(round(wager.iloc[i]['confidence']*100,2), round(wager.iloc[i]['win_profit'],2)))
        
        st.markdown("#### Total profit if all games hit: ${:.2f}".format(round(wager['win_profit'].sum(),2)))
        st.markdown("#### Probability of losing entire wager: {:.2f}%".format(round(prob_losing*100,2)))
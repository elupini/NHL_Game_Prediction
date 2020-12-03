# NHL_Game_Prediction
This project creates a selective betting model which can then be deployed as an app. The data is taken from Kaggle's NHL Dataset, and also uses the NHL API to fill in some gaps needed for advanced game statistics. When the NHL seasons begins, I will deploy the app.

Best way to use the repo is to run the code in each notebook. The betting notebook will finally produce a graph which displays how your predictive model did against a baseline. 

The stats downloaded through the NHL API are stored in the Data.zip, so you don't need to run the whole API call to collect the data (you can if you want and have a few hours to kill!)

The Data.zip DOES NOT contain the Kaggle data, so download from https://www.kaggle.com/martinellis/nhl-game-data and store all files in the Data directory. 

## File Structure
```
.
├── App
│   └── betting_app.py
├── Data.zip
├── Functions
│   ├── __init__.py
│   ├── api_functions.py
│   ├── app_functions.py
│   ├── betting_functions.py
│   ├── modelling_functions.py
│   └── preprocessing_functions.py
├── LICENSE
├── NHL_API
│   └── API.ipynb
├── Notebooks
│   ├── betting.ipynb
│   ├── modelling.ipynb
│   └── preprocessing_pipeline.ipynb
└── README.md
```
Enjoy!

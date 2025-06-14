import os
import django
import pandas as pd
from django.db import transaction
from django.db.models import Max
from predictor.models import PredictionModel
from games.models import Game
from django.utils import timezone
import pickle
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score
from predictor.ml_models.utils import GameDataFrameEntry

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "nhl_game_predictor_backend")
django.setup()

def generate_past_season_ids(past_seasons : list):
    """
    generates a list of the n past season IDs of the form 20XX20XX
    as required by the official NHL API
    """
    current_date = timezone.localdate()
    current_month = current_date.month
    current_year = current_date.year
    
    if current_month >= 7:  # July or later
        current_season_start_year = current_year
    else:  # January to June
        current_season_start_year = current_year - 1

    season_ids = []
    
    for i in range(past_seasons):
        year_start = current_season_start_year - (i + 1)
        season_id = f"{year_start}{year_start + 1}"
        season_ids.append(int(season_id))
    
    return season_ids

def create_seasons_dataframe(past_seasons : list):
    """
    creates a pandas dataframe of all games that took place in the
    list of seasons in past_seasons array of season IDs
    """
    # fetch all Game records for the specified past seasons
    games = Game.objects.filter(game_json__season__in=past_seasons).exclude(home_team_data=None, away_team_data=None)

    # create GameDataFrameEntry instances for each game
    game_dataframe_entries = [GameDataFrameEntry(game) for game in games]

    # convert the list of entries to a list of dictionaries
    game_data_dicts = [entry.to_dict() for entry in game_dataframe_entries]

    # create a DataFrame from the list of dictionaries
    game_data_df = pd.DataFrame(game_data_dicts)

    return game_data_df

def create_training_data(game_data_df : pd.DataFrame):
    """
    splits a pandas dataframe of game data into training and validation sets
    as required by the Random Forest model
    """
    # split features and labels from dataframe
    features = game_data_df.drop(columns=['home_team_win'])
    labels = game_data_df['home_team_win']

    # split of training and validation data
    return train_test_split(features, 
                            labels, 
                            test_size=0.2, 
                            random_state=31)

@transaction.atomic
def train_random_forest(past_seasons : list):
    """
    trains a new Random Forest model on the seasons in the past_seasons array.
    for example, calling train_random_forest([20242025, 20232024]) will train 
    a new Random Forest using data from the 2024-2025 and 2023-2024 NHL seasons
    """
    game_data_df = create_seasons_dataframe(past_seasons=past_seasons)

    training_features, testing_features, training_labels, testing_labels = create_training_data(game_data_df=game_data_df)

    # create random_forest (may have to test these parameters)
    random_forest = RandomForestClassifier(n_estimators=250, random_state=31, max_depth=15)

    # fit and predict
    random_forest.fit(training_features, training_labels)

    predicted_labels = random_forest.predict(testing_features)

    # evaluate accuracy
    accuracy = accuracy_score(testing_labels, predicted_labels)
    print("accuracy:", accuracy)

    # create a new prediction model object and save
    last_version = PredictionModel.objects.aggregate(Max('version'))['version__max']
    if last_version:
        major, minor = map(int, last_version.split('.'))
        new_version = f"{major}.{minor + 1}"
    else:
        new_version = "1.0"

    prediction_model = PredictionModel.objects.create(name="Random Forest", version=new_version)
    with open(f'./predictor/ml_models/trained_models/random-forest-v-{new_version.replace(".","-")}.pkl', 'wb') as file:
        pickle.dump(random_forest, file)

    print(f"Model Random Forest (v{new_version}) saved successfully.")
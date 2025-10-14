import os
import django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "nhl_game_predictor")
django.setup()

import pickle
import pandas as pd

from django.db import transaction
from games.models import Game, GamePrediction, TeamData
from predictor.ml_models.utils import GameDataFrameEntry, one_hot_encode_game_df
from predictor.models import PredictionModel
from predictor.ml_models.train_model import create_seasons_dataframe, create_training_data
from lime.lime_tabular import LimeTabularExplainer
from games.data_loader import load_team_data_for_date_from_api
from django.db.models.query import QuerySet

def load_random_forest_model():
    """
    loads latest trained model from the file system
    """

    # get latest PredictionModel
    latest_model = PredictionModel.objects.order_by('-version').first()
    if not latest_model:
        raise ValueError("No models found. Train a model first.")

    # get file path based 
    model_version = latest_model.version.replace(".", "-")
    model_path = f'./predictor/ml_models/trained_models/random-forest-v-{model_version}.pkl'

    # load the model
    with open(model_path, 'rb') as file:
        model = pickle.load(file)
    
    return model, latest_model

def get_top_features(game_data_frame_entry : GameDataFrameEntry, game_data_df : pd.DataFrame, model, training_features : pd.DataFrame) -> dict:
    """
    get the top 5 features driving the prediction outcome for a specific game
    """

    # use lime explainer. class_names is the label we're trying to predict
    explainer = LimeTabularExplainer(
        training_data=training_features.values,
        feature_names=training_features.columns.tolist(),
        class_names=['home_team_win'],
        mode='classification'
    )

    # get the prediction probabilities for the specific instance
    instance = game_data_df.iloc[0:1]
    _ = model.predict_proba(instance)

    # Explain the prediction
    exp = explainer.explain_instance(instance.values[0], model.predict_proba)

    # convert features into a list, and get their importance, and then clean the importances so feature values can be found
    top_features = sorted(exp.as_list(), 
                          key=lambda top_feature: abs(top_feature[1]),
                          reverse=True)
    
    game_feature_values = game_data_frame_entry.to_dict()

    cleaned_features = []

    for top_feature in top_features:
        tokens = top_feature[0].split(" ")
        importance_value = abs(top_feature[1])

        # we would only like to display positive feature values to the user for clarity
        if importance_value <= 0:
            break

        for token in tokens:
            if token in game_feature_values:
                cleaned_features.append([token, importance_value])
                break

        # exit if we have found the 5 most important features
        if len(cleaned_features) == 5:
            break

    top_features_dictionary = {cleaned_feature[0] : [game_feature_values[cleaned_feature[0]], cleaned_feature[1]] for cleaned_feature in cleaned_features}

    return top_features_dictionary

def predict_game_outcome(game : Game, model, training_features : pd.DataFrame) -> GamePrediction:
    """
    predict the outcome of a game using the latest Random Forest model.
    """
   
    # prepare game data for dataframe and prediction
    game_data_frame_entry = GameDataFrameEntry(game)
    game_data_df = pd.DataFrame([game_data_frame_entry.to_dict()])

    # one hot encode the dataframe
    game_data_df = one_hot_encode_game_df(game_data_df=game_data_df)

    # drop the label column (if included) for prediction
    if 'home_team_win' in game_data_df.columns:
        game_data_df = game_data_df.drop(columns=['home_team_win'])

    # make prediction
    prediction = model.predict(game_data_df)
    predicted_probability = model.predict_proba(game_data_df)[0]
    confidence = max(predicted_probability)
    predicted_home_team_win = True if prediction == 1 else False

    top_features = get_top_features(game_data_frame_entry=game_data_frame_entry,
                                    game_data_df=game_data_df,
                                    model=model,
                                    training_features=training_features)

    # get the latest model instance for saving prediction
    prediction_model = PredictionModel.objects.order_by('-version').first()
    if not prediction_model:
        raise ValueError("No trained model found. Train a model first.")

    game_prediction, _ = GamePrediction.objects.get_or_create(
        game=game,
        model=prediction_model,
        defaults={
            'predicted_home_team_win': predicted_home_team_win,
            'confidence_score': confidence,
            'top_features': top_features
        }
    )

    return game_prediction

@transaction.atomic
def predict_games(games : QuerySet[Game]) -> list:
    """
    function to create GamePredictions for all games on the current date
    """

    # Load the latest model
    model, model_object = load_random_forest_model()

    # obtain the entire seasons dataset for the most recent model
    trained_seasons = list(model_object.trained_seasons.values_list("id", flat=True))
    seasons_dataframe = create_seasons_dataframe(trained_seasons)

    # get training features
    training_features, _, _, _= create_training_data(seasons_dataframe)

    predictions = []
    team_data = []
    games_data = []
    for game in games:
        home_team_data = load_team_data_for_date_from_api(game.home_team, game.game_date)
        away_team_data = load_team_data_for_date_from_api(game.away_team, game.game_date)
        game.home_team_data = home_team_data
        game.away_team_data = away_team_data

        if home_team_data is not None:
            team_data.append(home_team_data)
        
        if away_team_data is not None:
            team_data.append(away_team_data)

        games_data.append(game)

        game_prediction = predict_game_outcome(game=game,
                                               model=model,
                                               training_features=training_features)
        predictions.append(game_prediction)

    # need to first create team data before bulk_updating the Games
    if team_data:
        TeamData.objects.bulk_create(team_data, ignore_conflicts=True)

        for td in team_data:
            if td.id is None:
                td.id = TeamData.objects.get(team=td.team, data_capture_date=td.data_capture_date).id
    
    if games_data:
        Game.objects.bulk_update(games_data, 
                                 fields=["home_team_data", "away_team_data"])
    
    return predictions


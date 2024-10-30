import pickle
import pandas as pd
from games.models import Game, GamePrediction
from predictor.ml_models.utils import GameDataFrameEntry
from predictor.models import PredictionModel
from predictor.ml_models.train_model import create_seasons_dataframe, create_training_data
from lime.lime_tabular import LimeTabularExplainer

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
    
    return model

def get_top_features(game_data_frame_entry : GameDataFrameEntry, game_data_df, model):
    """
    Get the top n features driving the prediction confidence for a specific game.
    """

    # get the data that was used to train the model (will need to update this in the PredictionModel class)
    training_features, _, _, _= create_training_data(create_seasons_dataframe([20222023,20232024]))

    # use lime explainer. class_names is the label we're trying to predict
    explainer = LimeTabularExplainer(
        training_data=training_features.values,
        feature_names=training_features.columns.tolist(),
        class_names=['home_team_win'],
        mode='classification'
    )

    # get the prediction probabilities for the specific instance
    instance = game_data_df.values[0] 
    _ = model.predict_proba(instance.reshape(1, -1))

    # Explain the prediction
    exp = explainer.explain_instance(instance, model.predict_proba)

    # get the top 5 features, their importance, and then clean the importances so feature values can be found
    top_features = exp.as_list()[:5]  # Get top 5 features
    top_features_df = pd.DataFrame(top_features, columns=['Feature', 'Importance'])


    top_features_df['Cleaned Feature'] = top_features_df['Feature'].apply(lambda feature: feature.split()[0])

    # get only the cleaned feature names and find corresponding feature values from game_data_frame_entry
    cleaned_features = top_features_df['Cleaned Feature'].tolist()
    game_feature_values = game_data_frame_entry.to_dict()
    top_features_dictionary = {}
    for cleaned_feature in cleaned_features:
        top_features_dictionary[cleaned_feature] = game_feature_values[cleaned_feature]

    return top_features_dictionary

def predict_game_outcome(game):
    """
    predict the outcome of a game using the latest Random Forest model.
    """
    # Load the latest model
    model = load_random_forest_model()

    # prepare game data for dataframe and prediction
    game_data_frame_entry = GameDataFrameEntry(game)
    game_data_df = pd.DataFrame([game_data_frame_entry.to_dict()])

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
                                    model=model)


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

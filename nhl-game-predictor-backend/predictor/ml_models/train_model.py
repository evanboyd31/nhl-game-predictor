import os
import django
from django.db import transaction
from django.db.models import Max
from predictor.models import PredictionModel
import pickle
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score
from predictor.ml_models.utils import create_seasons_dataframe, create_training_data

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "nhl_game_predictor_backend")
django.setup()

@transaction.atomic
def train_random_forest(past_seasons):
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
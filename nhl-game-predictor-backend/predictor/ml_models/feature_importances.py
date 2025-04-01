import django
import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from predictor.ml_models.utils import create_seasons_dataframe, create_features_and_labels

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "nhl_game_predictor")
django.setup()

def compute_cosine_similarities(features : pd.DataFrame, labels: pd.DataFrame):
  # standardize all feature columns and the labels to have mean of 0 and stddev of 1
  standardized_features = (features - features.mean()) / features.std()
  standardized_features.fillna(0, inplace=True)
  standardized_labels = (labels - labels.mean()) / labels.std()

  # compute the cosine similarity between all features and the label (home_team_win)
  feature_names = list(standardized_features.columns.values)
  cosine_similarities = {}
  for feature_name in feature_names:
    numpy_features = standardized_features[feature_name].to_numpy()
    numpy_labels = standardized_labels.to_numpy()
    wd = np.dot(numpy_features, numpy_labels) / numpy_features.size
    cosine_similarities[feature_name] = wd

  # sort and present the labels in a bar plot
  sorted_cosine_similarities = sorted(cosine_similarities.items(),
                                          key=lambda feature_wd: feature_wd[1],
                                          reverse=True) 
  plt.figure(figsize=(12, 12))
  plt.barh([feature_name for feature_name, _ in sorted_cosine_similarities],
          [coefficient for _, coefficient in sorted_cosine_similarities],
          color="#ee983a")
  plt.title("Cosine Similarity with Home Team Win")
  plt.xlabel("Cosine Similarity With Home Team Win")
  plt.ylabel("Feature Name")
  plt.gca().invert_yaxis()

  plt.savefig("predictor/ml_models/plots/cosine_similarity_plot.png", dpi=300, bbox_inches='tight')

  return sorted_cosine_similarities


def remove_irrelevant_features(past_seasons : list):
  game_data_df = create_seasons_dataframe(past_seasons=past_seasons)
  features, labels = create_features_and_labels(game_data_df=game_data_df)

  sorted_cosine_similarities = compute_cosine_similarities(features=features,
                                                           labels=labels)

  # find the features to remove based on the mean - stddev of absolute value cosine similarities
  absolute_cosine_similarities = [(name, abs(wd)) for name, wd in sorted_cosine_similarities]
  absolute_cosine_similarities.sort(key=lambda x: x[1],
                                        reverse=True)
  mean_absolute_regression_coefficient = np.mean(np.array([wd for _, wd in absolute_cosine_similarities]))
  stddev_absolute_regression_coefficient = np.std(np.array([wd for _, wd in absolute_cosine_similarities]))
  threshold = mean_absolute_regression_coefficient - stddev_absolute_regression_coefficient

  plt.figure(figsize=(12, 6))
  plt.bar([name for name, _ in absolute_cosine_similarities],
          [wd for _, wd in absolute_cosine_similarities],
          color="#ee983a")
  plt.axhline(y=threshold,
              color="black",
              label="Mean - Stddev")
  plt.xlabel("Feature Name")
  plt.ylabel("Absolute Cosine Similarity With Home Team Win")
  plt.title("Absolute Cosine Similarity With Home Team Win")
  plt.xticks(rotation=90)
  plt.legend()

  plt.savefig("predictor/ml_models/plots/absolute_cosine_similarity_plot.png", dpi=300, bbox_inches='tight')

  features_to_remove = [name for name, wd in absolute_cosine_similarities if wd < threshold]
  return pd.concat([features.drop(features_to_remove, axis=1), labels], axis=1)
  
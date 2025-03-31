import django
import os
import numpy as np
import matplotlib.pyplot as plt
from predictor.ml_models.utils import create_seasons_dataframe, create_features_and_labels

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "nhl_game_predictor")
django.setup()

def compute_cosine_similarities(past_seasons : list):
  game_data_df = create_seasons_dataframe(past_seasons=past_seasons)

  features, labels = create_features_and_labels(game_data_df=game_data_df)

  # standardize all feature columns and the labels to have mean of 0 and stddev of 1
  standardized_features = (features - features.mean()) / features.std()
  standardized_features.fillna(0, inplace=True)
  standardized_labels = (labels - labels.mean()) / labels.std()

  # compute the simple regression coefficient between all features and the label (home_team_win)
  feature_names = list(standardized_features.columns.values)
  regression_coefficients = {}
  for feature_name in feature_names:
    numpy_features = standardized_features[feature_name].to_numpy()
    numpy_labels = standardized_labels.to_numpy()
    wd = np.dot(numpy_features, numpy_labels) / numpy_features.size
    regression_coefficients[feature_name] = wd

  # sort and present the labels in a bar plot
  sorted_regression_coefficients = sorted(regression_coefficients.items(),
                                          key=lambda feature_wd: feature_wd[1],
                                          reverse=True) 
  plt.figure(figsize=(12, 12))
  plt.barh([feature_name for feature_name, _ in sorted_regression_coefficients],
          [coefficient for _, coefficient in sorted_regression_coefficients],
          color="#ee983a")
  plt.title("Cosine Similarity with Home Team Win")
  plt.xlabel("Cosine Similarity With Home Team Win")
  plt.ylabel("Feature Name")
  plt.gca().invert_yaxis()

  plt.savefig("predictor/ml_models/plots/cosine_similarity_plot.png", dpi=300, bbox_inches='tight')

  # find the features to remove based on the mean - stddev of absolute value cosine similarities
  absolute_regression_coefficients = [(name, abs(wd)) for name, wd in sorted_regression_coefficients]
  absolute_regression_coefficients.sort(key=lambda x: x[1],
                                        reverse=True)
  mean_absolute_regression_coefficient = np.mean(np.array([wd for _, wd in absolute_regression_coefficients]))
  stddev_absolute_regression_coefficient = np.std(np.array([wd for _, wd in absolute_regression_coefficients]))
  threshold = mean_absolute_regression_coefficient - stddev_absolute_regression_coefficient

  plt.figure(figsize=(12, 6))
  plt.bar([name for name, _ in absolute_regression_coefficients],
          [wd for _, wd in absolute_regression_coefficients],
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

  features_to_remove = [name for name, wd in absolute_regression_coefficients if wd < threshold]
  print(f"Names of features to remove: {features_to_remove}")
  
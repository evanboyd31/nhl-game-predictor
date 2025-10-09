from django.db import migrations
from predictor.ml_models.predict_model import get_model_feature_importances

def add_prediction_model_feature_importances(apps, schema_editor):
    PredictionModel = apps.get_model('predictor', 'PredictionModel')

    model_feature_importances = get_model_feature_importances()

    latest_model = PredictionModel.objects.order_by('-version').first()
    latest_model.feature_importances = model_feature_importances

    latest_model.save()

class Migration(migrations.Migration):

    dependencies = [
        ('predictor', '0004_predictionmodel_feature_importances'),
    ]

    operations = [
        migrations.RunPython(add_prediction_model_feature_importances)
    ]
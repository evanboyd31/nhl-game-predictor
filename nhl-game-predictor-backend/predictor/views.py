from rest_framework import generics
from rest_framework.views import APIView
from rest_framework.response import Response
from .models import PredictionModel
from .serializers import PredictionModelSerializer


class MostRecentPredictionModelDetailView(APIView):

  def get(self, request):
    latest_prediction_model = PredictionModel.objects.order_by('-version').first()
    serializer = PredictionModelSerializer(latest_prediction_model)

    return Response(serializer.data)
  

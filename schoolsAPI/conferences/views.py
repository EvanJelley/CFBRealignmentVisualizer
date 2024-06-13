from .serializers import ConferenceByYearSerializer
from .models import ConferenceByYear
from rest_framework import generics

class ConferenceByYearList(generics.ListAPIView):
    queryset = ConferenceByYear.objects.all()
    serializer_class = ConferenceByYearSerializer

class ConferenceByYearDetail(generics.RetrieveAPIView):
    queryset = ConferenceByYear.objects.all()
    serializer_class = ConferenceByYearSerializer
from .serializers import AllConferenceByYearSerializer 
from .models import ConferenceByYear
from rest_framework import generics

class AllConferenceByYearList(generics.ListAPIView):
    queryset = ConferenceByYear.objects.all()
    serializer_class = AllConferenceByYearSerializer

class ConferenceByYearDetail(generics.RetrieveAPIView):
    queryset = ConferenceByYear.objects.all()
    serializer_class = AllConferenceByYearSerializer
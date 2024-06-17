from .serializers import AllConferenceByYearSerializer, SpecificConferenceByYearSerializer 
from .models import ConferenceByYear
from rest_framework import generics

class AllConferenceByYearList(generics.ListAPIView):
    queryset = ConferenceByYear.objects.all()
    serializer_class = AllConferenceByYearSerializer

class ConferenceByYearListSEC(generics.ListAPIView):
    queryset = ConferenceByYear.objects.filter(conference__name='SEC')
    serializer_class = SpecificConferenceByYearSerializer

class ConferenceByYearDetail(generics.RetrieveAPIView):
    queryset = ConferenceByYear.objects.all()
    serializer_class = AllConferenceByYearSerializer
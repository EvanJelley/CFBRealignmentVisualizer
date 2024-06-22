from .serializers import AllConferenceByYearSerializer, ConferenceWithLogoSerializer, SchoolWithLogoSerializer
from .models import ConferenceByYear, ConferenceName, School
from rest_framework import generics

class AllConferenceByYearList(generics.ListAPIView):
    queryset = ConferenceByYear.objects.all()
    serializer_class = AllConferenceByYearSerializer

class ConferenceByYearDetail(generics.RetrieveAPIView):
    queryset = ConferenceByYear.objects.all()
    serializer_class = AllConferenceByYearSerializer

class ConferenceWithLogoList(generics.ListAPIView):
    queryset = ConferenceName.objects.all()
    serializer_class = ConferenceWithLogoSerializer

class SchoolWithLogoList(generics.ListAPIView):
    queryset = School.objects.all()
    serializer_class = SchoolWithLogoSerializer
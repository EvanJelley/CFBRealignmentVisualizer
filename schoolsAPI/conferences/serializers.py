from rest_framework import serializers
from .models import Conference, School, Year, ConferenceByYear

class ConferenceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Conference
        fields = ['id', 'name']

class SchoolSerializer(serializers.ModelSerializer):
    class Meta:
        model = School
        fields = ['id', 'name', 'city', 'state', 'latitude', 'longitude']

class YearSerializer(serializers.ModelSerializer):
    class Meta:
        model = Year
        fields = ['id', 'year']

class ConferenceByYearSerializer(serializers.ModelSerializer):
    conference = ConferenceSerializer()
    year = YearSerializer()
    school = SchoolSerializer(many=True)

    class Meta:
        model = ConferenceByYear
        fields = ['id', 'conference', 'year', 'school']

from rest_framework import serializers
from .models import School, Year, ConferenceByYear, ConferenceName


class SchoolSerializer(serializers.ModelSerializer):
    class Meta:
        model = School
        fields = ['id', 'name', 'city', 'state', 'latitude', 'longitude']

class YearSerializer(serializers.ModelSerializer):
    class Meta:
        model = Year
        fields = ['id', 'year']

class ConferenceNameSerializer(serializers.ModelSerializer):
    class Meta:
        model = ConferenceName
        fields = ['id', 'name']

class AllConferenceByYearSerializer(serializers.ModelSerializer):
    year = serializers.SerializerMethodField()
    schools = SchoolSerializer(many=True)
    conference = serializers.SerializerMethodField()

    class Meta:
        model = ConferenceByYear
        fields = ['id', 'year', 'schools', 'conference', 'football', 'basketball', 'centerLat', 'centerLon', 'capital', 'avgDistanceFromCenter', 'avgDistanceBetweenSchools']

    def get_year(self, obj):
        return obj.year.year
    
    def get_conference(self, obj):
        return obj.conference.name

class SpecificConferenceByYearSerializer(serializers.ModelSerializer):
    year = serializers.SerializerMethodField()
    schools = SchoolSerializer(many=True)

    class Meta:
        model = ConferenceByYear
        fields = ['id', 'year', 'schools', 'football', 'basketball', 'centerLat', 'centerLon', 'capital', 'avgDistanceFromCenter', 'avgDistanceBetweenSchools']
    
    def get_year(self, obj):
        return obj.year.year
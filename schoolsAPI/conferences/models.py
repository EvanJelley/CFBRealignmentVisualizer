from django.db import models
    
class School(models.Model):
    name = models.CharField(max_length=100)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=2)
    latitude = models.FloatField()
    longitude = models.FloatField()
    logo = models.ImageField(upload_to='images/school_logos', null=True, blank=True)

    def __str__(self):
        return self.name
    
class Year(models.Model):
    year = models.IntegerField()

    def __str__(self):
        return str(self.year)

class ConferenceName(models.Model):
    name = models.CharField(max_length=100)
    logo = models.ImageField(upload_to='images/conf_logos', null=True, blank=True)
    colors = models.JSONField(null=True, blank=True)
    historical = models.BooleanField(default=False)

    def __str__(self):
        return self.name

class MajorCity(models.Model):
    name = models.CharField(max_length=100)
    state = models.CharField(max_length=2)
    latitude = models.FloatField()
    longitude = models.FloatField()

    def __str__(self):
        return self.name


class ConferenceByYear(models.Model):
    # BASIC INFO
    year = models.ForeignKey(Year, on_delete=models.CASCADE)
    schools = models.ManyToManyField(School)
    conference = models.ForeignKey(ConferenceName, on_delete=models.CASCADE, null=True, blank=True)

    # SPORTS
    football = models.BooleanField(default=True)
    basketball = models.BooleanField(default=True)

    # GEOGRAPHY
    centerLat = models.FloatField(null=True, blank=True)
    centerLon = models.FloatField(null=True, blank=True)
    capital = models.ForeignKey(MajorCity, on_delete=models.CASCADE, null=True, blank=True)
    avgDistanceFromCenter = models.FloatField(null=True, blank=True)
    avgDistanceBetweenSchools = models.FloatField(null=True, blank=True)

    def __str__(self):
        return str(self.year.year) + ' ' + self.conference.name



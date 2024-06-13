from django.db import models

class Conference(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name
    
class School(models.Model):
    name = models.CharField(max_length=100)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=2)
    latitude = models.FloatField()
    longitude = models.FloatField()

    def __str__(self):
        return self.name
    
class Year(models.Model):
    year = models.IntegerField()

    def __str__(self):
        return str(self.year)
    
class ConferenceByYear(models.Model):
    year = models.ForeignKey(Year, on_delete=models.CASCADE)
    conference = models.ForeignKey(Conference, on_delete=models.CASCADE)
    school = models.ManyToManyField(School)
    
    def __str__(self):
        return str(self.year.year) + '_' + self.conference.name

from django.contrib import admin
from .models import Conference, School, Year, ConferenceByYear

admin.site.register(Conference)
admin.site.register(School)
admin.site.register(Year)
admin.site.register(ConferenceByYear)

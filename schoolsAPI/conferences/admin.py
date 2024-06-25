from django.contrib import admin
from .models import School, Year, ConferenceByYear, ConferenceName, MajorCity

admin.site.register(ConferenceName)
admin.site.register(School)
admin.site.register(Year)
admin.site.register(ConferenceByYear)
admin.site.register(MajorCity)


from django.urls import path
from .views import (
    AllConferenceByYearList, 
    ConferenceByYearDetail,
    ConferenceWithLogoList
    )


urlpatterns = [
    path('conferencebyyear/', AllConferenceByYearList.as_view()),
    path('conferencebyyear/<int:pk>/', ConferenceByYearDetail.as_view()),
    path('conferencelogos/', ConferenceWithLogoList.as_view())
]
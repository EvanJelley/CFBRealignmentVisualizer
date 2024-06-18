from django.urls import path
from .views import (
    AllConferenceByYearList, 
    ConferenceByYearDetail,
    )


urlpatterns = [
    path('conferencebyyear/', AllConferenceByYearList.as_view()),
    path('conferencebyyear/<int:pk>/', ConferenceByYearDetail.as_view()),
]
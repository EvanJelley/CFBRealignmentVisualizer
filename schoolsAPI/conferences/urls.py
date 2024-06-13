from django.urls import path
from .views import ConferenceByYearList, ConferenceByYearDetail

urlpatterns = [
    path('conferencebyyear/', ConferenceByYearList.as_view()),
    path('conferencebyyear/<int:pk>/', ConferenceByYearDetail.as_view()),
]
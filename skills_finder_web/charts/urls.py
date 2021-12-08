# Third part
from django.urls import path

# Own
from . import views

urlpatterns = [
    path("", views.MostWantedSkillsView.as_view(), name="show-chart"),
]

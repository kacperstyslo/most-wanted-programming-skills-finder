# Third part
from django.urls import path

# Own
from . import views

urlpatterns = [
    path("", views.JobsCategoriesView.as_view(), name="jobs-categories"),
]

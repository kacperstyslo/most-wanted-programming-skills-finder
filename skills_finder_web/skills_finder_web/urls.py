# Third part
from django.urls import path, include

urlpatterns = [
    path("", include("jobs.urls")),
    path("show-chart/", include("charts.urls")),
]

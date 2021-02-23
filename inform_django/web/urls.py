from django.urls import path
from . import views

urlpatterns = [
    path("", views.index),
    path("dashboards", views.dashboards),
    path("builder", views.builder),
]

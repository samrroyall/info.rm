from django.urls import path
from . import views

urlpatterns = [
    path("", views.home),
    path("dashboard/<int:season>", views.dashboard),
    path("league/<int:id>/<int:season>", views.leagues),
    path("team/<int:id>/<int:season>", views.teams),
    path("player/<int:id>/<int:season>", views.players),
    path("builder", views.builder),
    path("change_per_ninety", views.change_per_ninety),
]

from django.contrib import admin
from .models import Season, Country, League, Team, Player, PlayerStat

for model in [Season, Country, League, Team, Player, PlayerStat]:
    admin.site.register(model)
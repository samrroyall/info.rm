from django.db import models
from datetime import *

class Season(models.Model):
    start_year = models.IntegerField(unique=True)
    end_year = models.IntegerField(unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class Country(models.Model):
    name = models.CharField(max_length=255, unique=True)
    code = models.CharField(max_length=2, null=True)
    flag = models.CharField(max_length=255, null=True) # url
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class League(models.Model):
    league_id = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=255)
    league_type = models.CharField(max_length=255)
    logo = models.CharField(max_length=255) # url
    country = models.ForeignKey(Country, related_name="leagues", on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class Team(models.Model):
    class Meta: 
        unique_together = (('team_id', 'league', 'season'),)
    team_id = models.IntegerField()
    league = models.ForeignKey(League, related_name="teams", on_delete=models.CASCADE)
    season = models.ForeignKey(Season, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    logo = models.CharField(max_length=255) # url
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class Player(models.Model):
    player_id = models.IntegerField(primary_key=True)
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    age = models.IntegerField()
    height = models.CharField(max_length=10, null=True)
    weight = models.CharField(max_length=10, null=True)
    birthdate = models.DateField(null=True)
    nationality = models.ForeignKey(Country, related_name="players", on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class PlayerStat(models.Model):
    class Meta:
        unique_together = (('player', 'team'),)
    team = models.ForeignKey(Team, related_name="stats", on_delete=models.CASCADE)
    player = models.ForeignKey(Player, related_name="stats", on_delete=models.CASCADE)
    POSITIONS = [
        (1, "attacker"),
        (2, "midfielder"),
        (3, "defender"),
        (4, "goalkeeper"),
        (5, "none")
    ]
    DEFAULT_POSITION = 5
    position = models.PositiveSmallIntegerField(default=DEFAULT_POSITION, choices=POSITIONS)

    rating = models.DecimalField(max_digits=5, decimal_places=3)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    # shots
    shots = models.IntegerField()
    shots_on_target = models.IntegerField()
    # goals
    goals = models.IntegerField()
    goals_conceded = models.IntegerField()
    goals_saved = models.IntegerField()
    assists = models.IntegerField()
    # passes
    passes = models.IntegerField()
    passes_key = models.IntegerField()
    passes_accuracy = models.DecimalField(max_digits=4, decimal_places=3)
    # defense
    blocks = models.IntegerField()
    tackles = models.IntegerField()
    interceptions = models.IntegerField()
    duels = models.IntegerField()
    duels_won = models.IntegerField()
    # dribbles
    dribbles_attempted = models.IntegerField()
    dribbles_succeeded = models.IntegerField()
    # fouls
    fouls_drawn = models.IntegerField()
    fouls_committed = models.IntegerField()
    # cards
    yellows = models.IntegerField()
    reds = models.IntegerField()
    #penalties
    penalties_won = models.IntegerField() 
    penalties_committed = models.IntegerField() 
    penalties_scored = models.IntegerField() 
    penalties_taken = models.IntegerField() 
    penalties_saved = models.IntegerField() 
    # games
    appearances = models.IntegerField()
    starts = models.IntegerField()
    benches = models.IntegerField()
    minutes_played = models.IntegerField()
    substitutions_in = models.IntegerField()
    substitutions_out = models.IntegerField()
    # avgs and pcts 
    shots_on_target_pct = models.DecimalField(max_digits=4, decimal_places=3)
    duels_won_pct = models.DecimalField(max_digits=4, decimal_places=3)
    dribbles_succeeded_pct = models.DecimalField(max_digits=4, decimal_places=3)
    penalties_scored_pct = models.DecimalField(max_digits=4, decimal_places=3)

    @classmethod
    def get_position(cls, position_string):
        for n, position in cls.POSITIONS:
            if position == position_string.lower():
                return n
        return cls.DEFAULT_POSITION









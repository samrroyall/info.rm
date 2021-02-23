from django.db import models

class Season(models.Model):
    start_year = models.IntegerField()
    end_year = models.IntegerField()

class Country(models.Model):
    name = models.CharField(max_length=255)
    code = models.CharField(max_length=2)
    flag = models.CharField(max_length=255) # url
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class League(models.Model):
    primary_key = models.IntegerField()
    name = models.CharField(max_length=255)
    league_type = models.CharField(max_length=255)
    logo = models.CharField(max_length=255) # url
    country = models.ForeignKey(Country, related_name="leagues", on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class Team(models.Model):
    primary_key = models.IntegerField()
    name = models.CharField(max_length=255)
    logo = models.CharField(max_length=255) # url
    league = models.ForeignKey(League, related_name="teams", on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class Player(models.Model):
    primary_key = models.IntegerField()
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    age = models.IntegerField()
    height = models.CharField(max_length=10)
    weight = models.CharField(max_length=10)
    birth_date = models.DateField()
    nationality = models.ForeignKey(Country, related_name="players", on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class PlayerStat(models.Model):
    positions = [
        ("attacker", "attacker"),
        ("midfielder", "midfielder"),
        ("defender", "defender"),
        ("goalkeeper", "goalkeeper"),
    ]
    player = models.ForeignKey(Player, related_name="stats", on_delete=models.CASCADE)
    team = models.ForeignKey(Team, on_delete=models.CASCADE)
    league = models.ForeignKey(League, on_delete=models.CASCADE)
    season = models.ForeignKey(Season, on_delete=models.CASCADE)
    position = models.CharField(max_length=255, choices=positions)
    rating = models.DecimalField(max_digits=4, decimal_places=2)
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
    passes_accuracy = models.DecimalField(max_digits=4, decimal_places=1)
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
    shots_on_target_pct = models.DecimalField(max_digits=4, decimal_places=1)
    duels_won_pct = models.DecimalField(max_digits=4, decimal_places=1)
    dribbles_succeeded_pct = models.DecimalField(max_digits=4, decimal_places=1)
    penalties_scored_pct = models.DecimalField(max_digits=4, decimal_places=1)









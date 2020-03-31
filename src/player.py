from .query import get_player_data

player_keys = ["id", "league_id", "league_name", "team_id", "team_name", "name", "firstname", "lastname", "position", "age", "birth_date", "nationality", "flag", "height", "weight", "rating", "captain"]

player_stats_keys = ["shots", "shots_on", "shots_on_pct", "goals", "goals_conceded", "assists", "passes", "passes_key", "passes_accuracy", "tackles", "blocks", "interceptions", "duels", "duels_won", "duels_won_pct", "dribbles_past", "dribbles_attempted", "dribbles_succeeded", "dribbles_succeeded_pct", "fouls_drawn", "fouls_committed", "cards_yellow", "cards_red", "cards_second_yellow", "cards_straight_red", "penalties_won", "penalties_committed", "penalties_scored", "penalties_missed", "penalties_scored_pct", "penalties_saved", "games_appearances", "minutes_played", "games_started", "substitutions_in", "substitutions_out", "games_bench"]

team_keys = ["id", "league_id", "league_name", "name", "logo", "founded", "coach_name", "coach_firstname", "coach_lastname", "venue_name", "venue_city", "venue_capacity"]

league_keys = [ "id", "name", "type", "country", "season", "season_start", "season_end", "logo", "flag", "is_current"]

non_per90_stats = ["shots_on_pct", "passes_accuracy", "duels_won_pct", "dribbles_succeeded_pct", "cards_yellow", "cards_red", "cards_second_yellow", "cards_straight_red", "penalties_won", "penalties_committed", "penalties_scored", "penalties_missed", "penalties_scored_pct", "penalties_saved", "games_appearances", "minutes_played", "games_started", "substitutions_in", "substitutions_out", "games_bench"]

def player_team_data(player_id, season, per_90):
    player_data_dict = dict()
    player_stats_dict = dict()
    team_data_dict = dict()
    league_data_dict = dict()
    data = get_player_data(player_id, season)

    player_data = data[0]
    for i in range(len(player_data)):
        value = player_data[i]
        if i < len(player_keys):
            key = player_keys[i]
            player_data_dict[key] = value
        else:
            key = player_stats_keys[i - len(player_keys)]
            player_stats_dict[key] = value

    if per_90 is True:
        minutes_played = float(player_stats_dict.get("minutes_played"))
        for key in player_stats_dict.keys():
            if key not in non_per90_stats:
                current_val = player_stats_dict.get(key)
                if current_val is None:
                    player_stats_dict[key] = 0.0
                else:
                    player_stats_dict[key] = round(float(
                                                    player_stats_dict.get(key))/(minutes_played/90.0),
                                                    2
                                                )

    team_data = data[1]
    for i in range(len(team_data)):
        value = team_data[i]
        key = team_keys[i]
        team_data_dict[key] = value

    league_data = data[2]
    for i in range(len(league_data)):
        value = league_data[i]
        key = league_keys[i]
        league_data_dict[key] = value

    return player_data_dict, player_stats_dict, team_data_dict, league_data_dict

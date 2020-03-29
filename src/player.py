from .query import get_player_data

player_keys = ["id", "league_id", "league_name", "team_id", "team_name", "name", "firstname", "lastname", "position", "age", "birth_date", "nationality", "flag", "height", "weight", "rating", "captain"]

player_stats_keys = ["shots", "shots_on", "shots_on_pct", "goals", "goals_conceded", "assists", "passes", "passes_key", "passes_accuracy", "tackles", "blocks", "interceptions", "duels", "duels_won", "duels_won_pct", "dribbles_past", "dribbles_attempted", "dribbles_succeeded", "dribbles_succeeded_pct", "fouls_drawn", "fouls_committed", "cards_yellow", "cards_red", "cards_second_yellow", "cards_straight_red", "penalties_won", "penalties_committed", "penalties_scored", "penalties_missed", "penalties_scored_pct", "penalties_saved", "games_appearances", "minutes_played", "games_started", "substitutions_in", "substitutions_out", "games_bench"]

team_keys = ["id", "league_id", "league_name", "name", "logo", "founded", "coach_name", "coach_firstname", "coach_lastname", "venue_name", "venue_city", "venue_capacity"]

league_keys = [ "id", "name", "type", "country", "season", "season_start", "season_end", "logo", "flag", "is_current"]

def player_team_data(player_id):
    player_data_dict = dict()
    player_stats_dict = dict()
    team_data_dict = dict()
    league_data_dict = dict()
    data = get_player_data(player_id)

    player_data = data[0]
    for i in range(len(player_data)):
        value = player_data[i]
        if i < len(player_keys):
            key = player_keys[i]
            player_data_dict[key] = value
        else:
            key = player_stats_keys[i - len(player_keys)]
            player_stats_dict[key] = value

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

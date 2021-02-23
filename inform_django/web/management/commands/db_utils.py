# admin stuff
from django.core.management.base import BaseCommand
# python libraries
from datetime import date
import logging
from typing import List, Union
# project imports 
from .helpers.api import Request, Json
from .helpers.config import current_season, current_league_ids
from web.models import Season, Country, League, Team, Player, PlayerStat

class Command(BaseCommand):
    help="utilities for updating the database with API results"

    def handle(self, *args, **options):
        self.stdout.write("all good here.")

    def add_countries(self) -> None:
        country_response: List[Json] = Request(
            endpoint = "countries",
            params = {}
        )
        for country in country_response:
            if ("name" not in country or
                "code" not in country or
                "flag" not in country
            ):
                logging.error("Country response dictionary does not contain key 'name', 'code', and/or 'flag'.")
            # check whether country is in the database, if not, add it, if so, do nothing
            country_object: Country; created: bool
            country_object, created = Country.objects.get_or_create(
                name=country.get("name"), 
                code=country.get("code"), 
                flag=country.get("flag")
            )

    def add_leagues(self, season: int) -> None:
        league_response: List[Json] = Request(
            endpoint = "leagues",
            params = { "season": season }
        )
        for league in league_response:
            # ensure necessary keys exist in API response
            if "league" not in league or "id" not in league.get("league"):
                logging.error("League response dictionary does not contain key 'league' and/or 'league.id'.")
            # ensure that current league is in `current_league_ids`
            if league.get("league").get("id") not in current_league_ids:
                continue
            # ensure necessary keys exist in API response
            if ("country" not in league or 
                "name" not in league.get("country") or
                "code" not in league.get("country") or
                "flag" not in league.get("country") 
            ):
                logging.error("League response dictionary does not contain key 'country' and/or 'country.id/code/flag'.")
            # check if country is already in DB. 
            # if country is not in Country model, add it
            country_object: Country; created: bool
            country_object, created = Country.objects.get_or_create(
                name=league.get("country").get("name"),
                code=league.get("country").get("code"),
                flag=league.get("country").get("flag")
            )
            # ensure necessary keys exist in API response
            if ("id" not in league.get("league") or
                "name" not in league.get("league") or
                "type" not in league.get("league") or
                "logo" not in league.get("league") 
            ):
                logging.error("League response dictionary does not contain at least one of the following keys: 'league.id/name/type/logo'.")
            # check if league is already in DB.
            # if league is not in League model, add it, else, do nothing 
            league_object: League; created: bool 
            league_object, created = League.objects.get_create(
                primary_key=league.get("league").get("id"),
                name=league.get("league").get("name"),
                league_type=league.get("league").get("type"), 
                logo=league.get("league").get("logo"), 
                country=country_object
            )

    def add_teams(self, season: int) -> List[int]:
        current_team_ids: List[int] = [];
        for league_id in current_league_ids:
            teams_response: List[Json] = Request(
                endpoint = "teams",
                params = { 
                    "season": season,
                    "league": league_id
                },
            )
            for team in teams_response:
                # ensure necessary keys exist in API response
                if ("team" not in team or 
                    "id" not in team.get("team") or
                    "name" not in team.get("team") or 
                    "logo" not in team.get("team")
                ):
                    logging.error("Team response dictionary does not contain key 'team' and/or 'team.id/name/logo'.")
                try:
                    # get team's league foreign key
                    league_object: League = League.objects.get(primary_key=league_id)
                    # check if team is already in DB
                    # if team is not in Team model, add it, else, do nothing
                    team_object: Team; created: bool 
                    team_object, created = Team.objects.get_or_create(
                        primary_key=team.get("team").get("id"),
                        name=team.get("team").get("name"),
                        logo=team.get("team").get("logo"),
                        league=league_object
                    )
                    current_team_ids.append(team.get("team").get("id"))
                except League.DoesNotExist:
                    logging.error(f"League ({league_id}) is not present in the database, but is a member of `current_league_ids`.")
        return current_team_ids

    def not_null(self, value: Union[int, float]) -> Union[int, float]:
        return (value if value is not None else 0)

    def update_stats(self, player_object: Player, stats: List[Json]) -> None:
        if "league" not in stats or "id" not in stats.get("league"):
            logging.error("PlayerPlayerStat response dictionary does not contain key 'league' and/or 'league.id'.")
        league_object = League.objects.get(primary_key=stats.get("league").get("id"))
        if "team" not in stats or "id" not in stats.get("team"):
            logging.error("PlayerPlayerStat response dictionary does not contain key 'team' and/or 'team.id'.")
        team_object = Team.objects.get(primary_key=stats.get("team").get("id"))
        if (
            # league
            "season" not in stats.get("league") or
            # games
            "games" not in stats or
            "appearences" not in stats.get("games") or
            "lineups" not in stats.get("games") or
            "minutes" not in stats.get("games") or
            "position" not in stats.get("games") or
            "rating" not in stats.get("games") or
            # substitutes
            "substitutes" not in stats or
            "in" not in stats.get("substitutes") or
            "out" not in stats.get("substitutes") or
            "bench" not in stats.get("substitutes") or
            # shots
            "shots" not in stats or
            "total" not in stats.get("shots") or
            "on" not in stats.get("shots") or
            # goals
            "goals" not in stats or
            "total" not in stats.get("goals") or
            "conceded" not in stats.get("goals") or
            "saves" not in stats.get("goals") or
            "assists" not in stats.get("goals") or
            # passes
            "passes" not in stats or
            "total" not in stats.get("passes") or
            "key" not in stats.get("passes") or
            "accuracy" not in stats.get("passes") or
            # tackles
            "tackles" not in stats or
            "total" not in stats.get("tackles") or
            "blocks" not in stats.get("tackles") or
            "interceptions" not in stats.get("tackles") or
            # duels
            "duels" not in stats or
            "total" not in stats.get("duels") or
            "won" not in stats("duels") or
            # dribbles
            "dribbles" not in stats or
            "attempts" not in stats.get("dribbles") or
            "success" not in stats.get("dribbles") or
            # fouls
            "fouls" not in stats or
            "drawn" not in stats.get("fouls") or
            "committed" not in stats.get("fouls") or
            # cards
            "cards" not in stats or
            "yellow" not in stats.get("cards") or
            "red" not in stats.get("cards") or
            # penalty
            "penalty" not in stats or
            "won" not in stats.get("penalty") or
            "commited" not in stats.get("penalty") or
            "scored" not in stats.get("penalty") or
            "missed" not in stats.get("penalty") or
            "saved" not in stats.get("penalty")
        ):
            logging.error("PlayerPlayerStat dictionary does not contain one or more expected keys.")
        try:
            season_object: Season = Season.objects.get(start_year=stats.get("league").get("season"))
            playerstat_object: PlayerStat; created: bool 
            playerstat_object, created = PlayerStat.objects.update_or_create(
                player=player_object,
                team=team_object,
                league=league_object,
                season=season_object,
                position=stats.get("games").get("position").lower(),
                rating=float(self.not_null(stats.get("games").get("rating"))),
                # shots
                shots=self.not_null(stats.get("shots").get("total")),
                shots_on_target=self.not_null(stats.get("shots").get("on")),
                # goals
                goals=self.not_null(stats.get("goals").get("total")),
                goals_conceded=self.not_null(stats.get("goals").get("conceded")),
                goals_saved=self.not_null(stats.get("goals").get("saves")),
                assists=self.not_null(stats.get("goals").get("assists")),
                # passes
                passes=self.not_null(stats.get("passes").get("total")),
                passes_key=self.not_null(stats.get("passes").get("key")),
                passes_accuracy=self.not_null(stats.get("passes").get("accuracy")),
                # defense
                tackles=self.not_null(stats.get("tackles").get("total")),
                blocks=self.not_null(stats.get("tackles").get("blocks")),
                interceptions=self.not_null(stats.get("tackles").get("interceptions")),
                duels=self.not_null(stats.get("duels").get("total")),
                duels_won=self.not_null(stats.get("duels").get("won")),
                # dribbles
                dribbles_attempted=self.not_null(stats.get("dribbles").get("attempts")),
                dribbles_succeeded=self.not_null(stats.get("dribbles").get("success")),
                # fouls
                fouls_drawn=self.not_null(stats.get("fouls").get("drawn")),
                fouls_committed=self.not_null(stats.get("fouls").get("committed")),
                # cards
                yellows=self.not_null(stats.get("cards").get("yellow")),
                reds=self.not_null(stats.get("cards").get("red")),
                # penalties
                penalties_won=self.not_null(stats.get("penalty").get("won")), 
                penalties_committed=self.not_null(stats.get("penalty").get("commited")), 
                penalties_scored=self.not_null(stats.get("penalty").get("scored")), 
                penalties_taken=self.not_null(stats.get("penalty").get("scored")) + self.not_null(stats.get("penalty").get("missed")), 
                penalties_saved=self.not_null(stats.get("penalty").get("saved")), 
                # games
                appearances=self.not_null(stats.get("games").get("appearences")),
                starts=self.not_null(stats.get("games").get("lineups")),
                minutes=self.not_null(stats.get("games").get("minutes")),
                benches=self.not_null(stats.get("substitutes").get("bench")),
                substitutions_in=self.not_null(stats.get("substitutes").get("in")),
                substitutions_out=self.not_null(stats.get("substitutes").get("out")),
                # calculated stats
                shots_on_target_pct=(
                    float(self.not_null(stats.get("shots").get("on"))) / self.not_null(stats.get("shots").get("total"))
                    if self.not_null(stats.get("shots").get("total")) > 0
                    else None
                ),
                duels_won_pct=(
                    float(self.not_null(stats.get("duels").get("won"))) / self.not_null(stats.get("duels").get("total"))
                    if self.not_null(stats.get("duels").get("total")) > 0
                    else None
                ),
                dribbles_succeeded_pct=(
                    float(self.not_null(stats.get("dribbles").get("success"))) / self.not_null(stats.get("dribbles").get("attempts"))
                    if self.not_null(stats.get("dribbles").get("attempts")) > 0
                    else None
                ),
                penalties_scored_pct=(
                    float(self.not_null(stats.get("penalty").get("scored"))) / 
                    (self.not_null(stats.get("penalty").get("scored")) + self.not_null(stats.get("penalty").get("missed")))
                    if self.not_null(stats.get("penalty").get("scored")) + self.not_null(stats.get("penalty").get("missed")) > 0
                    else None
                ),
            )
        except Season.DoesNotExist:
            logging.error("Season pointed to in PlayerPlayerStat league key does not exist in database.")

    def handle_birthdate(self, date_str: str) -> date:
        try:
            return date.fromisoformat(date_str)
        except ValueError:
            seps = ['/', '\\', '.']
            # check different separation characters
            try:
                for sep in seps:
                    if sep in date_str:
                        return date.fromisoformat(date_str.replace(sep, '-'))
                logging.error(f"Invalid date format encountered: '{date_str}'.")
            except:
                # check different orderings
                try:
                    for sep in seps:
                        if sep in date_str:
                            split_date = date_str.split(sep)
                            if len(split_date != 3):
                                logging.error(f"Invalid date format encountered: '{date_str}'.")
                            try:
                                # DD-MM-YYYY
                                return date.fromisoformat(f"{split_date[2]}-{split_date[1]}-{split_date[0]}")
                            except:
                                try: 
                                    # MM-DD-YYYY
                                    return date.fromisoformat(f"{split_date[2]}-{split_date[0]}-{split_date[1]}")
                                except:
                                    try: 
                                        # YYYY-DD-MM
                                        return date.fromisoformat(f"{0}-{2}-{1}")
                                    except:
                                        logging.error(f"Invalid date format encountered: '{date_str}'.")
                except:
                    logging.error(f"Invalid date format encountered: '{date_str}'.")

    def update_players(self, season: int, current_team_ids: List[int]) -> None:
        for team_id in current_team_ids:
            player_response: List[Json] = Request(
                endpoint = "players",
                params = { 
                    "season": season,
                    "team": team_id
                }
            )
            for player in player_response:
                # ensure necessary keys exist in API response
                if ( "player" not in player or
                    "id" not in player.get("player") or
                    "first_name" not in player.get("player") or
                    "last_name" not in player.get("player") or
                    "age" not in player.get("player") or
                    "height" not in player.get("player") or
                    "weight" not in player.get("player") or
                    "nationality" not in player.get("player") or
                    "birth" not in player.get("player") or
                    "date" not in player.get("player").get("birth")
                ):
                    logging.error("Player response dictionary does not contain key 'player' and/or 'player.id/first_name/last_name/age/height/weight/nationality/birth/birth.date'.")
                # check if country is already in DB, if it is not, allow it to be null
                country_object: Union[Country, None] = None
                try:
                    country_object = Country.objects.get(name=player.get("player").get("nationality"))
                except Country.DoesNotExist:
                    logging.warning(f"Player nationality ({player.get('player').get('nationality')}) does not exist in database.")
                # check if player is already in DB
                # if player is not in Player model, add it, else, do nothing
                birthdate: date = self.handle_birthdate(player.get("player").get("birth").get("date"))
                player_object: Player; created: bool 
                player_object, created = Player.objects.get_or_create(
                    primary_key=player.get("player").get("id"),
                    first_name=player.get("player").get("first_name"),
                    last_name=player.get("player").get("last_name"),
                    age=player.get("player").get("age"),
                    height=player.get("player").get("height"),
                    weight=player.get("player").get("weight"),
                    nationality=country_object,
                    birth_date=birthdate
                )
                # ensure necessary initial keys exist in API response
                if ("statistics" not in player or
                    "games" not in player.get("statistics") or 
                    "minutes" not in player.get("statistics").get("games")
                ):
                    logging.error("Player response dictionary does not contain key 'statistics', 'statistics.games', and/or 'statistics.games.minutes'.")
                # update PlayerStat table if player had played at least a single minute
                minutes_played: int = player.get("statistics").get("games").get("minutes")
                if (minutes_played is None or minutes_played <= 0):
                    continue
                self.update_stats(player_object, player.get("statistics"))

    def update_db(self, season: int = current_season) -> None:
        self.add_leagues(season) # add leagues to DB from API
        current_team_ids = self.add_teams(season) # add teams to DB from API
        self.update_players(season, current_team_ids) # add players to and update player stats in DB from API

    def new_season(self, start_year: int) -> None:
        # add season to DB
        season_query: Season; created: bool
        season_query, created = Season.objects.get_or_create(
            start_year=start_year,
            end_year=start_year+1
        )
        self.add_countries() # check whether there are any new countries in database this season
        self.update_db() # add leagues, teams, players, and stats

# admin stuff
from django.core.management.base import BaseCommand
# python libraries
from datetime import date
import logging
from typing import List, Union, Tuple
# project imports 
from .helpers.api import Request, Json
from .helpers.config import current_season, initial_league_ids, LogLevel
from web.models import Season, Country, League, Team, Player, PlayerStat


class Command(BaseCommand):
    help="utilities for updating the database with API results"

    def add_arguments(self, parser):
        
        parser.add_argument(
            "routine",
            choices=["update-db", "new-season"],
            help="""new-season: add new season to DB and update countries. Takes requried -s/--start-year argument.
                update-db: update leagues, teams, players, and player stats. Takes optional -s/--start-year argument."""
        )

        parser.add_argument(
            "-s",
            "--start-year",
            type=str,
            required=False,
            help="Start year for season"
        )

        parser.add_argument(
            "--log-level",
            choices=["debug", "info", "warning", "error", "critical"],
            type=str,
            required=False,
            help="Logging level"
        )

    def handle(self, *args, **options):
        log_level_dict = {
            "debug": logging.DEBUG,
            "info": logging.INFO,
            "warning": logging.WARNING,
            "error": logging.ERROR,
            "critical": logging.CRITICAL
        }
        if options.get("log_level") is not None:
            self.log_level = log_level_dict.get(options.get("log_level"))
        else:
            self.log_level = logging.DEBUG
        logging.basicConfig(level=self.log_level)

        # ensure that `start_year` is formatted correctly
        start_year = options.get("start_year")
        assert start_year is None or (len(start_year) == 4 and start_year.isdigit()), \
            "manage.py db_utils: error: invalid format for following arguments: -s/--start-year"
        routine_str = options.get("routine")
        # ensure that `start_year` is not None if routine is `new-season`
        if routine_str == "new-season" and start_year is None:
            raise AssertionError(f"manage.py db_utils: error: routine 'new-season' missing the following required arguments: routine")
        # ensure that routine is either `new-season` or `update-db`
        if routine_str not in ["new-season", "update-db"]:
            raise AssertionError(f"manage.py db_utils: error: unrecognized value ('{routine_str}') provided for following arguments: routine")
        # and call routine with appropriate arguments
        routine = self.new_season if routine_str == "new-season" else self.update_db
        if start_year is not None:
            routine(int(start_year))
        else:
            routine()
    
    ######## ROUTINES ########

    def new_season(self, start_year: int) -> None:
        """ method to add new season to DB and update countries """
        self.add_season(start_year)
        self.add_countries() # check whether there are any new countries in database this season
        self.add_leagues(start_year, initial_league_ids) # add leagues to DB from API
        league_ids = [league.primary_key for league in League.objects.all().order_by("primary_key")]
        self.add_teams(start_year, league_ids) # add teams to DB from API

    def update_db(self, start_year: int = current_season) -> None:
        """ method to update leagues, teams, players, and player stats """
        current_team_ids = [team.primary_key for team in Team.objects.all().order_by("primary_key")]
        self.update_players(start_year, current_team_ids) # add players to and update player stats in DB from API

    ######## SEASON FUNCTION ########

    def add_season(self, start_year: int) -> Tuple[Season, bool]:
        season_object: Season; created: bool
        season_object, created = Season.objects.get_or_create(
            start_year=start_year,
            end_year=start_year+1
        )
        if created:
            logging.info(f"New Season object '{start_year}' encountered and created.")
        return season_object

    ######## COUNTRY FUNCTIONS ########

    def add_country(self, country: Json) -> Tuple[Country, bool]:
        if (
            "name" not in country or
            "code" not in country or
            "flag" not in country
        ):
            logging.error("Country response dictionary does not contain key 'name', 'code', and/or 'flag'.")
        # check whether country is in the database, if not, add it, if so, do nothing
        return Country.objects.get_or_create(
            name=country.get("name").lower(), 
            code=( 
                country.get("code").upper() 
                if "code" in country and country.get("code") is not None 
                else None
            ), 
            flag=(
                country.get("flag").lower() 
                if "flag" in country and country.get("flag") is not None
                else None 
            ) 
        )

    def add_countries(self) -> None:
        country_response: List[Json] = Request(
            endpoint = "countries",
            params = {}
        ).request()
        countries_created: int = 0
        for country in country_response:
            try: 
                country_created: Country; created: bool
                country_object, created = self.add_country(country)    
                countries_created += created
            except Exception as e:
                logging.warning(f"Country object was not created.\n\tCountry: {country}\n\tException: {e}")
        logging.info(f"{countries_created} new Country objects created.")

    ######## LEAGUE FUNCTIONS ########

    def add_league(self, league: Json) -> Tuple[League, bool]:
        # ensure necessary keys exist in API response
        if ("country" not in league):
            logging.error("League response dictionary does not contain key 'country' and/or 'country.id/code/flag'.")
        # check if country is already in DB. 
        # if country is not in Country model, add it
        country_object: Country; created: bool
        country_object, created = self.add_country(league.get("country"))
        if created:
            logging.info(f"New Country object '{league.get('country').get('name')}' encountered and created.")
        # ensure necessary keys exist in API response
        if ("id" not in league.get("league") or
            "name" not in league.get("league") or
            "type" not in league.get("league") or
            "logo" not in league.get("league") 
        ):
            logging.error("League response dictionary does not contain at least one of the following keys: 'league.id/name/type/logo'.")
        # check if league is already in DB.
        # if league is not in League model, add it, else, do nothing 
        return League.objects.get_or_create(
            primary_key=league.get("league").get("id"),
            name=league.get("league").get("name").lower(),
            league_type=league.get("league").get("type").lower(), 
            logo=league.get("league").get("logo").lower(), 
            country=country_object
        )

    def add_leagues(self, season: int, league_ids: List[int]) -> None:
        league_response: List[Json] = Request(
            endpoint = "leagues",
            params = { "season": season }
        ).request()
        leagues_created: int = 0
        for league in league_response:
            # ensure necessary keys exist in API response
            if "league" not in league or "id" not in league.get("league"):
                logging.error("League response dictionary does not contain key 'league' and/or 'league.id'.")
                continue
            # ensure that current league is in `league_ids`
            if league.get("league").get("id") not in league_ids:
                continue
            try:
                league_object: League; created: bool 
                league_object, created = self.add_league(league)
                leagues_created += created
            except Exception as e:
                logging.warning(f"League object was not created.\n\tLeague: {league}\n\tException: {e}")
        logging.info(f"{leagues_created} new League objects created.")

    ######## TEAM FUNCTIONS ########

    def add_team(self, season: int, team: Json, league_id: int) -> Tuple[Team, bool]:
        # ensure necessary keys exist in API response
        if ("team" not in team or 
            "id" not in team.get("team") or
            "name" not in team.get("team") or 
            "logo" not in team.get("team")
        ):
            logging.error("Team response dictionary does not contain key 'team' and/or 'team.id/name/logo'.")
        # get team's league foreign key
        try:
            league_object: League = League.objects.get(primary_key=league_id)
        except Exception as e:
            logging.error(f"League object (id={league_id}) reference by new Team object was not found.")
        # get team's season foreign key
        season_object: Season = self.add_season(season)
        # check if team is already in DB
        # if team is not in Team model, add it, else, do nothing
        return Team.objects.get_or_create(
            primary_key=team.get("team").get("id"),
            name=team.get("team").get("name").lower(),
            logo=team.get("team").get("logo").lower(),
            season=season_object,
            league=league_object
        )

    def add_teams(self, season: int, league_ids: List[int]) -> List[int]:
        current_team_ids: List[int] = [];
        teams_created: int = 0
        for league_id in league_ids:
            teams_response: List[Json] = Request(
                endpoint = "teams",
                params = { 
                    "season": season,
                    "league": league_id
                },
            ).request()
            for team in teams_response:
                try:
                    team_object: Team; created: bool
                    team_object, created = self.add_team(season, team, league_id) 
                    teams_created += created
                    current_team_ids.append(team.get("team").get("id"))
                except Exception as e:
                    logging.warning(f"Team object was not created.\n\tTeam: {team}\n\tException: {e}")
        logging.info(f"{teams_created} new Team objects created.")
        return current_team_ids

    ######## PLAYER FUNCTIONS ########

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

    def update_player(self, player: Json) -> Tuple[Player, bool]:
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
        # check if country is already in DB, if it is not, create it
        country_object: Country; created: bool = False
        try:
            country_object: Country = Country.objects.get(name=player.get("player").get("nationality"))
        except Country.DoesNotExist:
            country_object, created = self.add_country({
                "country": { 
                    "name": player.get("player").get("nationality") 
                }
            }) 
            logging.info(f"New Country object '{player.get('player').get('nationality')}' encountered and created.")
        # check if player is already in DB
        # if player is not in Player model, add it, else, do nothing
        birthdate: date = self.handle_birthdate(player.get("player").get("birth").get("date"))
        return Player.objects.get_or_create(
            primary_key=player.get("player").get("id"),
            first_name=player.get("player").get("first_name").lower(),
            last_name=player.get("player").get("last_name").lower(),
            age=player.get("player").get("age"),
            height=player.get("player").get("height").lower(),
            weight=player.get("player").get("weight").lower(),
            nationality=country_object,
            birthdate=birthdate
        )

    def update_players(self, season: int, current_team_ids: List[int]) -> None:
        for team_id in current_team_ids:
            player_response: List[Json] = Request(
                endpoint = "players",
                params = { 
                    "season": season,
                    "team": team_id
                }
            ).request()
            players_created: int = 0
            playerstats_created: int = 0
            playerstats_updated: int = 0
            for player in player_response:
                # ensure necessary initial keys exist in API response
                if ("statistics" not in player or
                    "games" not in player.get("statistics") or 
                    "minutes" not in player.get("statistics").get("games")
                ):
                    logging.critical("Player response dictionary does not contain key 'statistics', 'statistics.games', and/or 'statistics.games.minutes'.")
                    continue
                # only handle players that have played at least a single minute
                minutes_played: int = player.get("statistics").get("games").get("minutes")
                if (minutes_played is None or minutes_played <= 0): continue
                # update or create Player object
                try:
                    player_object: Player; created: bool 
                    player_object, created = self.update_player(player)
                    players_created += created
                except Exception as e:
                    logging.warning(f"Player object was not created.\n\tPlayer: {player}\n\tException: {e}")
                    continue
                # update or create PlayerStat object
                try:
                    stat_created = self.update_stats(player_object, player.get("statistics"))
                    playerstats_created += stat_created
                    playerstats_updated += not stat_created 
                except Exception as e:
                    logging.warning(f"PlayerStat object was not created.\n\tPlayerStat: {player.get('statistics')}\n\tException: {e}")
            logging.info(f"{players_created} new Player objects created for Team (id={team_id}).")
            logging.info(f"{playerstats_created} new PlayerStat objects created for Team (id={team_id}).")
            logging.info(f"{playerstats_updated} new PlayerStat objects updated for Team (id={team_id}).")

    ######## PLAYERSTAT FUNCTIONS ########

    def not_null(self, value: Union[int, float]) -> Union[int, float]:
        return (value if value is not None else 0)

    def update_stats(self, player_object: Player, stats: List[Json]) -> bool:
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
        season_object: Season = self.add_season(stats.get("league").get("season"))
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
        return created

    
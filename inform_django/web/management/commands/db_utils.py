# admin stuff
from django.core.management.base import BaseCommand
# python libraries
from datetime import date
import logging
from types import SimpleNamespace
from typing import Dict, List, Union, Tuple
# project imports 
from .helpers.api import Request, Json
from .helpers.config import initial_league_ids, LogLevel
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
        if options["log_level"] is not None:
            self.log_level = log_level_dict[ options["log_level"] ]
        else:
            self.log_level = logging.DEBUG
        logging.basicConfig(level=self.log_level)

        # ensure that `start_year` is formatted correctly
        start_year = options["start_year"]
        assert start_year is None or (len(start_year) == 4 and start_year.isdigit()), \
            "manage.py db_utils: error: invalid format for following arguments: -s/--start-year"
        routine_str = options["routine"]
        # ensure that `start_year` is not None if routine is `new-season`
        if routine_str == "new-season" and start_year is None:
            raise AssertionError(f"manage.py db_utils: error: routine 'new-season' missing the following required arguments: -s/--start-year")
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
        season_object = self.add_season(start_year)
        self.add_countries() # check whether there are any new countries in database this season
        self.add_leagues(season_object, initial_league_ids) # add leagues to DB from API
        league_objects = list(League.objects.all().order_by("league_id"))
        self.add_teams(season_object, league_objects) # add teams to DB from API

    def update_db(self, start_year: Union[int, None] = None) -> None:
        """ method to update leagues, teams, players, and player stats """
        if start_year == None:
            seasons = Season.objects.all().order_by("-start_year")
            if len(seasons) == 0:
                raise AssertionError(f"manage.py db_utils: error: routine 'new-season' must be run prior to 'update-db'.")
            start_year = seasons[0].start_year
        season_object = self.add_season(start_year)
        league_ids = [ league.league_id for league in League.objects.all() ]
        team_ids = list( set( [ team.team_id for team in Team.objects.filter(season=season_object) ] ) )
        self.update_players(season_object, team_ids, league_ids) # add players to and update player stats in DB from API

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
            logging.warning("Country response dictionary does not contain key 'name', 'code', and/or 'flag'.")
        # check whether country is in the database, if not, add it, if so, do nothing
        return Country.objects.get_or_create(
            name=country["name"].lower(), 
            code=( 
                country["code"].upper() 
                if "code" in country and country["code"] is not None 
                else None
            ), 
            flag=(
                country["flag"].lower() 
                if "flag" in country and country["flag"] is not None
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
            logging.error("League response dictionary does not contain key 'country' and/or 'country.name/code/flag'.")
        # check if country is already in DB. 
        # if country is not in Country model, add it
        country_object: Country; created: bool
        country_object, created = self.add_country(league["country"])
        if created:
            logging.info(f"New Country object '{league['country']['name']}' encountered and created.")
        # ensure necessary keys exist in API response
        if (
            "id" not in league["league"] or
            "name" not in league["league"] or
            "type" not in league["league"] or
            "logo" not in league["league"] 
        ):
            logging.error("League response dictionary does not contain at least one of the following keys: 'league.id/name/type/logo'.")
        # check if league is already in DB.
        # if league is not in League model, add it, else, do nothing 
        return League.objects.get_or_create(
            league_id=league["league"]["id"],
            name=league["league"]["name"].lower(),
            league_type=league["league"]["type"].lower(), 
            logo=league["league"]["logo"].lower(), 
            country=country_object
        )

    def add_leagues(self, season_object: Season, league_ids: List[int]) -> None:
        league_response: List[Json] = Request(
            endpoint = "leagues",
            params = { "season": season_object.start_year }
        ).request()
        leagues_created: int = 0
        for league in league_response:
            # ensure necessary keys exist in API response
            if "league" not in league or "id" not in league["league"]:
                logging.error("League response dictionary does not contain key 'league' and/or 'league.id'.")
                continue
            # ensure that current league is in `league_ids`
            if league["league"]["id"] not in league_ids:
                continue
            try:
                league_object: League; created: bool 
                league_object, created = self.add_league(league)
                leagues_created += created
            except Exception as e:
                logging.warning(f"League object was not created.\n\tLeague: {league}\n\tException: {e}")
        logging.info(f"{leagues_created} new League objects created.")

    ######## TEAM FUNCTIONS ########

    def add_team(
        self, 
        season_object: Season, 
        league_object: League,
        team: Json, 
    ) -> Tuple[Team, bool]:
        # ensure necessary keys exist in API response
        if (
            "team" not in team or 
            "id" not in team["team"] or
            "name" not in team["team"] or 
            "logo" not in team["team"]
        ):
            logging.error("Team response dictionary does not contain key 'team' and/or 'team.id/name/logo'.")
        # check if team is already in DB
        # if team is not in Team model, add it, else, do nothing
        return Team.objects.get_or_create(
            team_id=team["team"]["id"],
            name=team["team"]["name"].lower(),
            logo=team["team"]["logo"].lower(),
            season=season_object,
            league=league_object
        )

    def add_teams(
        self, 
        season_object: Season, 
        league_objects: List[League]
    ) -> List[int]:
        current_team_ids: List[int] = [];
        teams_created: int = 0
        for league_object in league_objects:
            teams_response: List[Json] = Request(
                endpoint = "teams",
                params = { 
                    "season": season_object.start_year,
                    "league": league_object.league_id
                },
            ).request()
            for team in teams_response:
                try:
                    team_object: Team; created: bool
                    team_object, created = self.add_team(season_object, league_object, team) 
                    teams_created += created
                    current_team_ids.append(team["team"]["id"])
                except Exception as e:
                    logging.warning(f"Team object was not created.\n\tTeam: {team}\n\tException: {e}")
        logging.info(f"{teams_created} new Team objects created.")
        return current_team_ids

    ######## PLAYER FUNCTIONS ########

    def not_null(
        self, 
        value: Union[int, float, None], 
        default: Union[int, float] = 0
    ) -> Union[int, float]:
        return value if value is not None else default

    def divide_not_null(
        self, 
        numerator: Union[int, float, None], 
        denominator: Union[int, float, None], 
    ) -> Union[int, float]:
        not_null_numerator = float(self.not_null(numerator))
        not_null_denominator = float(self.not_null(denominator))
        return (
            not_null_numerator/not_null_denominator
            if not_null_denominator > 0
            else 0.0
        )

    def handle_birthdate(self, date_str: Union[str, None]) -> date:
        try:
            return date.fromisoformat(date_str) if date_str is not None else None
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
        if ( 
            "id" not in player or
            "firstname" not in player or
            "lastname" not in player or
            "age" not in player or
            "height" not in player or
            "weight" not in player or
            "nationality" not in player or
            "birth" not in player or
            "date" not in player["birth"]
        ):
            logging.error("Player response dictionary does not contain one of the following keys 'player.id/first_name/last_name/age/height/weight/nationality/birth/birth.date'.")
        # check if country is already in DB, if it is not, create it
        country_object: Country; created: bool = False
        try:
            country_object: Country = Country.objects.get(name=player["nationality"].lower())
        except Country.DoesNotExist:
            country_object, created = self.add_country({
                "name": player["nationality"] 
            }) 
            logging.info(f"New Country object '{player['nationality'].lower()}' encountered and created.")
        # check if player is already in DB,, if it is not, add it
        birthdate: date = self.handle_birthdate(player["birth"]["date"])
        return Player.objects.get_or_create(
            player_id=player["id"],
            first_name=player["firstname"].lower(),
            last_name=player["lastname"].lower(),
            age=player["age"],
            height=player["height"].lower() if player["height"] is not None else None,
            weight=player["weight"].lower() if player["weight"] is not None else None,
            nationality=country_object,
            birthdate=birthdate
        )

    def update_players(
        self, 
        season_object: Season, 
        current_team_ids: List[Team], 
        current_league_ids: List[int]
    ) -> None:
        for team_id in current_team_ids:
            player_response: List[Json] = Request(
                endpoint = "players",
                params = { 
                    "season": season_object.start_year,
                    "team": team_id
                }
            ).request()
            # initialize player/playerstats created/updated vars
            players_created: int = 0
            playerstats_created: int = 0
            playerstats_updated: int = 0
            for player in player_response:
                if "player" not in player:
                    logging.error("Player response dictionary does not contain keys 'player'.")
                # update or create Player object
                try:
                    player_object: Player; created: bool 
                    player_object, created = self.update_player(player["player"])
                    players_created += created
                except Exception as e:
                    logging.warning(f"Player object was not created.\n\tPlayer: {player['player']}\n\tException: {e}")
                    continue

                # ensure player response contains a statistics key
                if "statistics" not in player:
                    logging.error("Player response dictionary does not contain key 'statistics'.")
                # ensure player statistics key references a list
                if not isinstance(player["statistics"], list):
                    logging.error(f"Player.statistics key in response is of type: {type(player['statistics'])}.")

                # grab all statistics for the player that are associated with a tracked league 
                for player_stats in player["statistics"]:
                    # ensure each player_stat is a dictionary
                    if not isinstance(player_stats, dict):
                        logging.error(f"A member of the Player.statistics list is of type: {type(player_stats)}.")
                    # ensure player statistics dict contains key league and league.id
                    if "league" not in player_stats or "id" not in player_stats["league"]:
                        logging.error("Member of Player.statistics list does not contain key 'league' and/or 'league.id'.")
                    # ensure player.statistics.league.id exists and is a league of interest 
                    if player_stats["league"]["id"] not in current_league_ids:
                        continue

                    # ensure player statistics dict contains key games and games.minutes
                    if "games" not in player_stats or "minutes" not in player_stats["games"]:
                        logging.error("Member of Player.statistics list does not contain key 'games' and/or 'games.minutes'.")
                    # ensure player.statistics.games.minutes exists and is greater than 0
                    if self.not_null( player_stats["games"]["minutes"] ) == 0: 
                        continue

                    # create league object
                    league_object = League.objects.get(league_id=player_stats["league"]["id"])
                    # create team object
                    try:
                        team_object = Team.objects.get(team_id=team_id, season=season_object, league=league_object)
                    except Exception as e:
                        logging.warning(f"PlayerStat objects was not created.\n\tteam: {team_id}, league: {league_object.league_id}\n\tException: {e}")
                        continue
                    # update or create PlayerStat object
                    try:
                        stat_created = self.update_stats(team_object, player_object, player_stats)
                        playerstats_created += stat_created
                        playerstats_updated += not stat_created 
                    except Exception as e:
                        logging.warning(f"PlayerStat object was not created.\n\tPlayer: {player['player']}\n\tPlayerStat: {player_stats['league']}\n\tException: {e}")
            logging.info(f"{players_created} new Player objects created for Team (team_id={team_object.team_id}).")
            logging.info(f"{playerstats_created} new PlayerStat objects created for Team (team_id={team_object.team_id}).")
            logging.info(f"{playerstats_updated} new PlayerStat objects updated for Team (team_id={team_object.team_id}).")

    ######## PLAYERSTAT FUNCTIONS ########
        
    def check_stats_keys(
        self, 
        data_name: str,
        data: Json,
        keys: List[str]
    ) -> None:
        for key in keys:
            if key not in data:
                logging.error(f"PlayerStat response missing key '{data_name}.{key}'.")

    def update_stats(
        self, 
        team_object: Team,
        player_object: Player, 
        player_stats: Dict[str, Json]
    ) -> bool:
        # create simple namespace out of player_stats Json object
        stats = SimpleNamespace(**player_stats) 
        # check stats.games keys
        self.check_stats_keys( "stats.games", stats.games, [ "appearences", "lineups", "minutes", "position", "rating" ])
        # check stats.substitutes keys
        self.check_stats_keys( "stats.substitutes", stats.substitutes, [ "in", "out", "bench" ])
        # check stats.shots keys
        self.check_stats_keys( "stats.shots", stats.shots, [ "total", "on" ])
        # check stats.goals keys
        self.check_stats_keys( "stats.goals", stats.goals, [ "total", "conceded", "assists", "saves" ])
        # check stats.passes keys
        self.check_stats_keys( "stats.passes", stats.passes, [ "total", "key", "accuracy" ])
        # check stats.tackles keys
        self.check_stats_keys( "stats.tackles", stats.tackles, [ "total", "blocks", "interceptions" ])
        # check stats.duels keys
        self.check_stats_keys( "stats.duels", stats.duels, [ "total", "won" ])
        # check stats.dribbles keys
        self.check_stats_keys( "stats.dribbles", stats.dribbles, [ "attempts", "success" ])
        # check stats.fouls keys
        self.check_stats_keys( "stats.fouls", stats.fouls, [ "drawn", "committed" ])
        # check stats.cards keys
        self.check_stats_keys( "stats.cards", stats.cards, [ "yellow", "red" ])
        # check stats.penalty keys
        self.check_stats_keys( "stats.penalty", stats.penalty, [ "won", "commited", "scored", "missed", "saved" ])
        # create new PlayerStat object
        playerstat_object: PlayerStat; created: bool 
        playerstat_object, created = PlayerStat.objects.update_or_create(
            # foreign keys 
            team=team_object,
            player=player_object,
            # player data
            position=PlayerStat.get_position( stats.games["position"] ),
            rating=self.not_null( stats.games["rating"], 0.0 ),
            # shots
            shots=self.not_null( stats.shots["total"] ),
            shots_on_target=self.not_null( stats.shots["on"] ),
            # goals
            goals=self.not_null( stats.goals["total"] ),
            goals_conceded=self.not_null( stats.goals["conceded"] ),
            goals_saved=self.not_null( stats.goals["saves"] ),
            assists=self.not_null( stats.goals["assists"] ),
            # passes
            passes=self.not_null( stats.passes["total"] ),
            passes_key=self.not_null( stats.passes["key"] ),
            passes_accuracy=float(self.not_null( stats.passes["accuracy"] ))/100,
            # defense
            tackles=self.not_null( stats.tackles["total"] ),
            blocks=self.not_null( stats.tackles["blocks"] ),
            interceptions=self.not_null( stats.tackles["interceptions"] ),
            duels=self.not_null( stats.duels["total"] ),
            duels_won=self.not_null( stats.duels["won"] ),
            # dribbles
            dribbles_attempted=self.not_null( stats.dribbles["attempts"] ),
            dribbles_succeeded=self.not_null( stats.dribbles["success"] ),
            # fouls
            fouls_drawn=self.not_null( stats.fouls["drawn"] ),
            fouls_committed=self.not_null( stats.fouls["committed"] ),
            # cards
            yellows=self.not_null( stats.cards["yellow"] ),
            reds=self.not_null( stats.cards["red"] ),
            # penalties
            penalties_won=self.not_null( stats.penalty["won"] ), 
            penalties_committed=self.not_null( stats.penalty["commited"] ), 
            penalties_scored=self.not_null( stats.penalty["scored"] ), 
            penalties_taken=self.not_null( stats.penalty["scored"] ) + self.not_null( stats.penalty["missed"] ), 
            penalties_saved=self.not_null( stats.penalty["saved"] ), 
            # games
            appearances=self.not_null( stats.games["appearences"] ),
            starts=self.not_null( stats.games["lineups"] ),
            minutes_played=self.not_null( stats.games["minutes"] ),
            benches=self.not_null( stats.substitutes["bench"] ),
            substitutions_in=self.not_null( stats.substitutes["in"] ),
            substitutions_out=self.not_null( stats.substitutes["out"] ),
            # calculated stats
            shots_on_target_pct=self.divide_not_null( stats.shots["on"], stats.shots["total"] ),
            duels_won_pct=self.divide_not_null( stats.duels["won"], stats.duels["total"] ),
            dribbles_succeeded_pct=self.divide_not_null( stats.dribbles["success"], stats.dribbles["attempts"] ),
            penalties_scored_pct=self.divide_not_null( 
                stats.penalty["scored"], 
                self.not_null( stats.penalty["scored"] ) + self.not_null( stats.penalty["missed"] )
            )
        )
        return created

    
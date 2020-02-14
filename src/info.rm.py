from .request import Request

########################
#### UPDATE METHODS ####
########################

def update_leagues(request):
    """ Function for updating leagues data from API and storing in DB
        Parameters:
            season :: current season, pulled from config file
    """
    request_class = request()
    league_data = request_class.update()
    # db.store_response(orm_instances)

    return league_ids

def update_teams(request, league_ids):
    """ Function for updating teams data from API and storing in DB
        Parameters:
            leagues :: current watched leagues, pulled from DB
    """
    request_class = request(endpoint=f"teams/league/")
    for league_id in league_ids:
        team_data = request_class.update(parameter=f"{league_id}", foreign_key=league_id)
        # db.store_response(orm_instances)

    return team_ids

def update_players(request, team_ids):
    """ Function for updating players data from API and storing in DB
        Parameters:
            season :: current season, pulled from config file
            teams  :: teams from current watched leagues, pulled from DB
    """
    request_class = request(endpoint="players/team/")
    for team_id in team_ids:
        player_data = request_class.update(paramter=f"{team_id}/{season}", foreign_key=team_id))
        # db.store_response(orm_instances)

    return

def config(token, sub_hour, sub_minute, season, leagues):
    """ Function for writing CLI arguments to config file.
        Parameters:
            token      :: API token to be used for future responses
            sub_hour   :: Hour current API subscription began
            sub_minute :: Minute current API subscription began
            season     :: Start year of current season (e.g. 2019, for the 2019-2020 season)
            leagues    :: Leagues to be watched
    """

def main(**kwargs)
    """ info.rm.py's main function.
        action :: desired procedure
            config
            update_all
            update_leagues
            update_teams
            update_players
    """
    action = kwargs.get("action")
    if action == "config":
    else:
        if kwargs.get("action") == "update_all":

            
        else:
            request = Request._REGISTRY.get(f"{action.split('_')[1].capitalize()}Request")
    pass 

# utilize argparse
if __name__ == "__main__":
    main()

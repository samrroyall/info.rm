from .request import Request

########################
#### UPDATE METHODS ####
########################

def update_leagues(season):
    ''' Function for updating leagues data from API and storing in DB
    '''
    leagues_request = Request(endpoint=f"leagues/season/{season}", type="Leagues")
    orm_instances = leagues_request.update()
    # db.store_response(orm_instances)

    pass

def update_teams(leagues):
    ''' Function for updating teams data from API and storing in DB
    '''
    teams_request = Request(endpoint=f"teams/league/", type="Teams")
    for league in leagues:
        orm_instances = teams_request.update(parameter=f"{league.id}", id=league.id)
        # db.store_response(orm_instances)

    pass

def update_players(season, teams):
    ''' Function for updating players data from API and storing in DB
    '''
    players_request = Request(endpoint="players/team/", type="Players")
    for team in teams:
        orm_instances = players_request.update(paramter=f"{team.id}/{season}", id=team.id)
        # db.store_response(orm_instances)

    pass

def main()
    ''' info.rm's main function, which performs the action specified by the end user.
        Actions:
            update_leagues :: updates league data from API
                Parameters:
                    season - current season, pulled from config file
            update_teams :: updates team data from API
                Parameters:
                    leagues - current watched leagues, pulled from DB
            update_players :: updates player data from API
                Parameters:
                    season - current season, pulled from config file
                    teams  - teams from current watched leagues, pulled from DB
            setup :: one-time action done at setup, which creates config file and DB
                Parameters:
                    token      - API token to be used for future responses
                    sub_hour   - Hour current API subscription began
                    sub_minute - Minute current API subscription began
                    season     - Start year of current season (e.g. 2019, for the 2019-2020 season)
                    leagues    - Leagues to be watched
    '''

    pass

if __name__ == "__main__":
    main()

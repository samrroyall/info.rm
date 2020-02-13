from .request import Request

########################
#### UPDATE METHODS ####
########################

def update_leagues(season):
    ''' Function for updating leagues data from API and storing in DB
    '''
    leagues_request = Request(endpoint=f"leagues/season/{season}", type="Leagues")
    leagues_request.update()

def update_teams(leagues):
    ''' Function for updating teams data from API and storing in DB
    '''
    teams_request = Request(endpoint=f"teams/league/", type="Teams")
    for league in leagues:
        teams_request.update(f"{league.id}")

def update_players(season, teams):
    ''' Function for updating players data from API and storing in DB
    '''
    players_request = Request(endpoint="players/team/", type="Players")
    for team in teams:
        players_request.update(f"{team.id}/{season}")

def main()
    '''
    '''

if __name__ == "__main__":
    main()

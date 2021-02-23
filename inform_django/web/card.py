from typing import Union
import models

class CardList:
    def __init__(self, title: str, cards: List[Card]) -> None:
        self.title = title
        self.cards = cards

class Card:
    def __init__(self, 
        title: str,
        data: Union[List[DashCardEntry], List[BuilderCardEntry]]
    ) -> None:
        self.title = title
        self.data = data
    
    def get_pages(self) -> List[Union[List[DashCardEntry], List[BuilderCardEntry]]]:
        num_pages = ceil(len(self.data)/10)
        pages = []
        for i in range(num_pages):
            start = i*10
            end = (i+1)*10 if (i+1)*10 <= len(self.data) else len(self.data)
            pages.append( self.data[start, end] )

class DashCardEntry:
    def __init__(self, 
        rank: int,
        value: Union[int, float],
        first_name: models.Players.first_name, 
        last_name: models.Player.last_name,
        team: models.Teams.name, 
        team_logo: models.Teams.logo
    ) -> None:
        self.rank = rank
        self.value = value
        self.first_name = first_name
        self.last_name = last_name
        self.team = team
        self.team_logo = team_logo

class BuilderCardEntry:
    def __init__(self, 
        rank_to_values: Dict[int, Union[int, float]],
        first_name: models.Players.first_name, 
        last_name: models.Player.last_name,
        team: models.Teams.name, 
        team_logo: models.Teams.logo,
        league: models.Leagues.name
    ) -> None:
        self.rank_to_values = this.rank_to_values,
        self.first_name = first_name
        self.last_name = last_name
        self.team = team
        self.team_logo = team_logo
        self.league = league

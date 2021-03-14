from django.db.models import FloatField, IntegerField, QuerySet
import math
from typing import Union, List, Callable, Any

from .models import PlayerStat
from .queryset import order_queryset, filter_queryset, initial_queryset 

class CardEntry:
    def __init__(
        self, 
        value: Union[int, float, str],
        playerstat: PlayerStat
    ) -> None:
        self.value = value
        self.data = playerstat

    @classmethod
    def display_float(cls, value: float, pct: bool) -> str:
        pct_string = str( round(100*round(value, 3)) )
        float_string = str( round(value,3) ).split('.')
        return ( 
            f"{pct_string}%" if pct is True
            else float_string[0] + '.' + float_string[1][:2].ljust(2, '0')
        )

class DashCardEntry(CardEntry):
    def __init__(
        self, 
        value: Union[int, float],
        playerstat: PlayerStat,
        rank: int
    ) -> None:
        super(value, playerstat)
        self.rank = rank
        self.player_id = self.data.player.player_id
        self.first_name = self.data.player.first_name
        self.last_name = self.data.player.last_name
        self.team = self.data.team.name
        self.team_id = self.data.team.team_id
        self.team_logo = self.data.team.logo
        self.league = self.data.team.league.name

    def get_player_name(self):
        return f"{self.first_name[0].upper()}. {self.last_name.title()}"
    
class Card:
    def __init__(
        self, 
        title: str,
        data: List[CardEntry]
    ) -> None:
        self.title = title
        self.data = data
        self.num_pages = math.ceil(len(self.data)/10)
    
    def get_pages(self) -> List[ List[CardEntry] ]:
        pages = []
        for i in range(self.num_pages):
            start = i*10
            end = (i+1)*10 if (i+1)*10 <= len(self.data) else len(self.data)
            pages.append( self.data[start:end] )
        return pages

class DashCard(Card):
    def __init__(
        self, 
        title: str,
        data: List[DashCardEntry]
    ) -> None:
        super(title, data)

    @classmethod
    def format_data( 
        cls,
        queryset: QuerySet, 
        per_ninety: bool,
        pct: bool
    ) -> List[DashCardEntry]:
        entries = []
        prev_val = None
        prev_rank = None
        curr_rank = 0
        for playerstat in queryset:
            curr_rank += 1
            val = playerstat.order_field
            rank = curr_rank if (prev_val is None or prev_val != val) else prev_rank
            prev_rank = rank 
            prev_val = val
            entries.append(DashCardEntry(
                rank=rank, 
                value=DashCardEntry.display_float(val, pct) if type(val) != int else val, 
                playerstat=playerstat
            ))
        return entries

    @classmethod
    def from_queryset(
        cls,
        queryset: QuerySet,
        per_ninety: bool,
        field: Union[str, IntegerField, FloatField],
        title: Union[str, None] = None,
        desc: bool = True,
        pct: bool = False,
        filter_lambdas: List[Callable] = []
    ) -> Any:
        filtered_queryset = filter_queryset(queryset, filter_lambdas)
        ordered_queryset = order_queryset(filtered_queryset, field, per_ninety, desc)
        title = field.replace('_',' ').title() if title is None else title
        return DashCard(
            title=title if per_ninety is False else f"{title} Per 90", 
            data=cls.format_data(ordered_queryset, per_ninety, pct)
        )

class StatCard(Card):
    def __init__(
        self, 
        title: str,
        data: List[CardEntry]
    ) -> None:
        self.title = title
        self.data = data
        self.num_pages = math.ceil(len(self.data)/10)

    @classmethod
    def from_playerstat(playerstat: PlayerStat):
        pass

class BioCard(Card):
    def __init__(
        self, 
        data: List[CardEntry]
    ) -> None:
        self.title = "Bio"
        self.data = data
        self.num_pages = math.ceil(len(self.data)/10)
    
    @classmethod
    def from_playerstat(playerstat: PlayerStat):
        pass

class CardList:
    def __init__(self, cards: List[Card]) -> None:
        self.cards = cards

# class BuilderCardEntry:
#     def __init__(self, 
#         rank_to_values: Dict[int, Union[int, float]],
#         player_stat: PlayerStat
#     ) -> None:
#         self.rank_to_values = this.rank_to_values,
#         self.first_name = player_stat.player.first_name
#         self.last_name = player_stat.player.last_name
#         self.team = player_stat.team.name
#         self.team_logo =  player_stat.team.logo
#         self.league = player_stat.league.name

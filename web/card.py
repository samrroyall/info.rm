from django.db.models import FloatField, IntegerField, QuerySet
import math
from typing import Any, Callable, Dict, List, Union

from .models import PlayerStat
from .queryset import order_queryset, modify_queryset

#############################
######## CARDENTRY ##########
#############################

class CardEntry:
    def __init__(
        self, 
        title: str,
        value: Union[int, float, str, None]
    ) -> None:
        self.title = title
        self.value = value

    @classmethod
    def display_float(cls, value: float, pct: bool) -> str:
        pct_string = str( round(100*round(value, 3)) )
        float_string = str( round(value,3) ).split('.')
        return ( 
            f"{pct_string}%" if pct is True
            else float_string[0] + '.' + float_string[1][:2].ljust(2, '0')
        )

class BioCardEntry(CardEntry):
    def __init__(
        self, 
        title: str,
        value: Union[int, float],
        logo: Union[str, None] = None,
        link: Union[str, None] = None
    ) -> None:
        super().__init__(title, value)
        self.logo = logo
        self.link = link

class DashCardEntry(CardEntry):
    def __init__(
        self, 
        value: Union[int, float],
        data: PlayerStat,
        rank: int
    ) -> None:
        super().__init__("", value)
        self.data = data
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

class BuilderCardEntry(CardEntry):
    def __init__(
        self, 
        values: Dict[str, Union[int, float]],
        data: PlayerStat,
        rank: int
    ) -> None:
        super().__init__("", None)
        self.values = values
        self.data = data
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

#############################
########### CARD ############
#############################
    
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

    @classmethod
    def from_list(
        cls,
        title: str,
        per_ninety: bool,
        minutes_played: int,
        stats: List[Dict[str, Union[str, float, int]]]
    ) -> Any:
        entries = []
        for stat in stats: 
            format_per_ninety = per_ninety is True and ("per_ninety" not in stat or stat["per_ninety"] is True)
            formatted_title = stat["title"] + " Per 90" if format_per_ninety is True else stat["title"]
            pct = ("pct" in stat and stat["pct"] is True)
            if format_per_ninety:
                formatted_value = CardEntry.display_float(float(stat["value"])*90/float(minutes_played), pct)
            elif type(stat["value"]) == float or pct is True:
                formatted_value = CardEntry.display_float(float(stat["value"]), pct)
            else:
                formatted_value = stat["value"]
            entries.append( CardEntry(title=formatted_title, value=formatted_value) )
        return Card(
            title=title,
            data=entries
        )

class BioCard(Card):
    def __init__(
        self, 
        data: List[BioCardEntry]
    ) -> None:
        super().__init__("Bio", data)
    
    @classmethod
    def from_playerstat(cls, playerstat: PlayerStat):
        data = []
        data.append(BioCardEntry(
            title="Position",
            value=playerstat.get_position_display().title(),
        ))
        data.append(BioCardEntry(
            title="Team",
            value=playerstat.team.name.title(),
            logo=playerstat.team.logo,
            link=f"/team/{playerstat.team.team_id}/"
        ))
        data.append(BioCardEntry(
            title="League",
            value=playerstat.team.league.name.title(),
            logo=playerstat.team.league.logo,
            link=f"/league/{playerstat.team.league.league_id}/"
        ))
        data.append(BioCardEntry(
            title="Nationality",
            value=playerstat.player.nationality.name.title(),
            logo=playerstat.player.nationality.flag
        ))
        birthdate = playerstat.player.birthdate
        birthdate_str = birthdate.strftime(f"%B {birthdate.day}, %Y")
        data.append(BioCardEntry(
            title="Date of Birth",
            value=f"{birthdate_str} ({playerstat.player.age})",
        ))
        height_in = float(playerstat.player.height[:-3])*0.3937008
        data.append(BioCardEntry(
            title="Height",
            value=f"{math.floor(height_in/12)}'{round(height_in % 12)}''"
        ))
        weight_lb = float(playerstat.player.weight[:-3])*2.204623
        data.append(BioCardEntry(
            title="Weight",
            value=f"{round(weight_lb)} lbs"
        ))
        return BioCard(data=data)
    
class DashCard(Card):
    def __init__(
        self, 
        title: str,
        data: List[DashCardEntry]
    ) -> None:
        super().__init__(title, data)

    @classmethod
    def format_data( 
        cls,
        queryset: QuerySet, 
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
                value=CardEntry.display_float(val, pct) if type(val) != int else val, 
                data=playerstat
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
        lambdas: List[Callable] = []
    ) -> Any:
        filtered_queryset = modify_queryset(queryset, lambdas)
        ordered_queryset = order_queryset(filtered_queryset, field, per_ninety, desc)
        title = field.replace('_',' ').title() if title is None else title
        return DashCard(
            title=title if per_ninety is False else f"{title} Per 90", 
            data=cls.format_data(ordered_queryset, per_ninety, pct)
        )

class BuilderCard(Card):
    def __init__(
        self, 
        header: List[str], 
        data: List[BuilderCardEntry]
    ) -> Any:
        super().__init__("Query Results", data)
        self.header = header

    @classmethod
    def format_data( 
        cls,
        queryset: QuerySet, 
        select_fields: Dict[str, Union[FloatField, IntegerField, bool]],
        order_by_field: Dict[str, Union[FloatField, IntegerField, bool]]
        # pct: bool
    ) -> List[BuilderCardEntry]:
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
            entries.append(
                BuildCardEntry(
                    rank=rank, 
                    values=select_fields, # consider how to display floats/pcts
                    data=playerstat
                )
            )
        return entries



    @classmethod
    def from_queryset(
        cls,
        queryset: QuerySet,
        select_fields: Dict[str, Union[FloatField, IntegerField, bool]],
        order_by_field: Dict[str, Union[FloatField, IntegerField, bool]],
        lambdas: List[Callable] = []
    ) -> Any:
        filtered_queryset = modify_queryset(queryset, lambdas)
        ordered_queryset = order_queryset(
            filtered_queryset, 
            order_by_field["value"], 
            order_by_field["per_ninety"], 
            order_by_field["desc"]
        )
        return BuilderCard(
            header=select_fields.keys(),
            data=cls.format_data(ordered_queryset, select_fields, order_by_field)
        )

class CardList:
    def __init__(self, cards: List[Card]) -> None:
        self.cards = cards

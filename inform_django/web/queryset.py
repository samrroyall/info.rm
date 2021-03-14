from django.db.models import F, FloatField, IntegerField, QuerySet, Max
from django.db.models.functions import Cast 
from typing import Callable, List, Union

from .management.commands.helpers.config import top_five_league_ids
from .models import Season, League, PlayerStat

def get_max( queryset: QuerySet, field: str ) -> QuerySet:
    return float( list(queryset.aggregate( Max(field) ).values())[0] )

def order_queryset(
    queryset: QuerySet, 
    field: Union[str, IntegerField, FloatField],
    per_ninety: bool,
    desc: bool,
    limit: int = 50
) -> QuerySet:
    per_ninety_value = Cast(F("minutes_played"), FloatField())/90.0
    field_value = field if type(field) != str else F(field)
    order_value = field_value if per_ninety is False else Cast(field_value, FloatField())/per_ninety_value 
    # may need to filter queryset more for per90 cards
    return queryset.annotate(order_field=order_value).order_by(
        "-order_field" if desc is True else "order_field"
    )[:limit]

def filter_queryset( 
    queryset: QuerySet, 
    lambdas: List[Callable] 
) -> QuerySet:
    for l in lambdas:
        queryset = l(queryset)
    return queryset

def initial_queryset(
    current_season: Season,
    league: Union[League, None]
) -> QuerySet:
    # get valid leagues
    valid_leagues = [ 
        league if league is not None
        else League.objects.get(league_id=id) for id in top_five_league_ids 
    ]
    # get valid queryset based on leagues, season, and minutes_played
    return filter_queryset(
        PlayerStat.objects.all(),
        [
            lambda q: q.filter(team__season=current_season),
            lambda q: q.filter(team__league__in=valid_leagues),
            lambda q: q.filter(minutes_played__gte=get_max(q, "minutes_played")/5)
        ]
    )


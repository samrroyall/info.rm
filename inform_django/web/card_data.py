from django.db.models import F, FloatField, QuerySet
from django.db.models.functions import Cast 
from typing import Dict, List, Union

from .card import Card, DashCard, StatCard, BioCard, CardList
from .models import Season, League, Player, PlayerStat
from .queryset import get_max

card_cache = {
    # '{League.league_id}-{Season.start_year}-{per_ninety}' -> List[ CardList ]
}

def card_cache_key(season: Season, per_ninety: bool, league: League) -> str:
    league_str = "Top5" if league is None else league.league_id
    return f"{league_str}-{season.start_year}-{per_ninety}"

def get_from_cache(season: Season, per_ninety: bool, league: League) -> List[CardList]:
    return card_cache.get(card_cache_key(season, per_ninety, league))

def insert_to_cache(season: Season, per_ninety: bool, league: League, data: List[CardList]) -> None:
    card_cache[card_cache_key(season, per_ninety, league)] = data

def get_dashboard_data(queryset: QuerySet, per_ninety: bool) -> List[CardList]:
    # GOALS CARDS
    goals_card = DashCard.from_queryset(
        queryset=queryset,
        per_ninety=per_ninety,
        field="goals"
    )
    assists_card = DashCard.from_queryset(
        queryset=queryset,
        per_ninety=per_ninety,
        field="assists"
    )
    goal_contributions_card = DashCard.from_queryset(
        queryset=queryset,
        per_ninety=per_ninety,
        field=F("goals")+F("assists"),
        title="Goal Contributions"
    )
    goals_per_shot_card = DashCard.from_queryset(
        queryset=queryset,
        per_ninety=False,
        field=Cast(F("goals"), FloatField())/Cast(F("shots"), FloatField()),
        title="Goals Per Shot",
        filter_lambdas=[lambda q: q.filter( shots__gte=get_max(q, "shots")/5 )]
    )
    shots_card = DashCard.from_queryset(
        queryset=queryset,
        per_ninety=per_ninety,
        field="shots"
    )
    shots_on_target_card = DashCard.from_queryset(
        queryset=queryset,
        per_ninety=per_ninety,
        field="shots_on_target"
    )
    # PASSES CARDS
    key_passes_card = DashCard.from_queryset(
        queryset=queryset,
        per_ninety=per_ninety,
        field="passes_key",
        title="Key Passes"
    )
    passes_card = DashCard.from_queryset(
        queryset=queryset,
        per_ninety=per_ninety,
        field="passes"
    )
    pass_accuracy_card = DashCard.from_queryset(
        queryset=queryset,
        per_ninety=False,
        field="passes_accuracy",
        title="Pass Accuracy",
        pct=True,
        filter_lambdas=[lambda q: q.filter( passes__gte=get_max(q, "passes")/5 )]
    )
    # DRIBBLES CARDS
    successful_dribbles_card = DashCard.from_queryset(
        queryset=queryset,
        per_ninety=per_ninety,
        field="dribbles_succeeded",
        title="Successful Dribbles"
    )
    attempted_dribbles_card = DashCard.from_queryset(
        queryset=queryset,
        per_ninety=per_ninety,
        field="dribbles_attempted",
        title="Attempted Dribbles"
    )
    dribble_success_rate_card = DashCard.from_queryset(
        queryset=queryset,
        per_ninety=False,
        field="dribbles_succeeded_pct",
        title="Dribble Success Rate",
        pct=True,
        filter_lambdas=[
            lambda q: q.filter(
                dribbles_attempted__gte=get_max(q, "dribbles_attempted")/5 
            )
        ]
    )
    # DEFENSIVE CARDS
    tackles_card = DashCard.from_queryset(
        queryset=queryset,
        per_ninety=per_ninety,
        field="tackles"
    )
    interceptions_card = DashCard.from_queryset(
        queryset=queryset,
        per_ninety=per_ninety,
        field="interceptions"
    )
    blocks_card = DashCard.from_queryset(
        queryset=queryset,
        per_ninety=per_ninety,
        field="blocks"
    )
    # EXTRA CARDS
    rating_card = DashCard.from_queryset(
        queryset=queryset,
        per_ninety=False,
        field="rating",
        title="Player Rating"
    )
    goals_conceded_card = DashCard.from_queryset(
        queryset=queryset,
        per_ninety=True,
        field="goals_conceded",
        desc=False,
        filter_lambdas=[
            lambda q: q.filter(position=PlayerStat.get_position("goalkeeper")),
            lambda q: q.filter(minutes_played__gte=get_max(q, "minutes_played")/4)
        ]
    )
    penalties_saved_card = DashCard.from_queryset(
        queryset=queryset,
        per_ninety=False,
        field="penalties_saved"
    )

    return [
        CardList([ goals_card, assists_card, goal_contributions_card, goals_per_shot_card ]),
        CardList([ shots_card, shots_on_target_card ]),
        CardList([ key_passes_card, passes_card, pass_accuracy_card ]),
        CardList([ successful_dribbles_card, attempted_dribbles_card, dribble_success_rate_card ]),
        CardList([ tackles_card, interceptions_card, blocks_card ] ),
        CardList([ rating_card, goals_conceded_card, penalties_saved_card ])
    ]

def get_player_data(playerstats: List[PlayerStat]) -> Dict[str, Card]:
    # create bio card
    bio_card = BioCard.from_playerstat(playerstats)
    # create player stat card
    stat_card = StatCard.from_playerstat(playerstats)
    return {
        "bio": bio_card,
        "stats": stat_card
    }
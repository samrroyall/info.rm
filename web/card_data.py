from django.db.models import F, FloatField, QuerySet
from django.db.models.functions import Cast 
from typing import Dict, List, Union

from .card import Card, DashCard, BioCard, CardList
from .models import Season, League, Player, PlayerStat
from .queryset import get_max

#################################
#####   CACHE AND HELPERS   #####
#################################

card_cache = {
    # '{League.league_id}-{Season.start_year}-{per_ninety}' -> List[ CardList ]
}

def clear_cache() -> None:
    card_cache = {}

def card_cache_key(season: Season, per_ninety: bool, league: League) -> str:
    league_str = "Top5" if league is None else league.league_id
    return f"{league_str}-{season.start_year}-{per_ninety}"

def get_from_cache(season: Season, per_ninety: bool, league: League) -> List[CardList]:
    return card_cache.get(card_cache_key(season, per_ninety, league))

def insert_to_cache(season: Season, per_ninety: bool, league: League, data: List[CardList]) -> None:
    card_cache[card_cache_key(season, per_ninety, league)] = data

#################################
####   CARD DATA FUNCTIONS   ####
#################################

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
        lambdas=[lambda q: q.filter( shots__gte=get_max(q, "shots")/5 )]
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
        lambdas=[lambda q: q.filter( passes__gte=get_max(q, "passes")/5 )]
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
        lambdas=[
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
        lambdas=[
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

def get_player_data(
    playerstat: PlayerStat,
    per_ninety: bool
) -> Dict[str, List[CardList]]:
    player_data = {}
    # create bio card
    player_data["bio"] = CardList([
        BioCard.from_playerstat(playerstat) 
    ])
    # create player stat card
    attacking_card = Card.from_list(
        title="Scoring",
        per_ninety=per_ninety,
        minutes_played=playerstat.minutes_played,
        stats=[
            { "title": "Goals", "value": playerstat.goals },
            { 
                "title": "Goals Per Shot",
                "value": float(playerstat.goals)/playerstat.shots if playerstat.goals > 0 else 0.0,
                "per_ninety": False,
            },
            { "title": "Shots On Target", "value": playerstat.shots_on_target },
            { "title": "Shots", "value": playerstat.shots },
            { 
                "title": "Shots On Target %", 
                "value": playerstat.shots_on_target_pct, 
                "per_ninety": False,
                "pct": True
            },
            { "title": "Penalties Scored", "value": playerstat.penalties_scored },
            { "title": "Penalties Taken", "value": playerstat.penalties_taken },
            { 
                "title": "Penalty Success Rate", 
                "value": playerstat.penalties_scored_pct,
                "per_ninety": False,
                "pct": True,
            }, 
        ]
    )
    creation_card = Card.from_list(
        title="Attacking",
        per_ninety=per_ninety,
        minutes_played=playerstat.minutes_played,
        stats=[
            { "title": "Assists", "value": playerstat.assists },
            { "title": "Passes", "value": playerstat.passes },
            { "title": "Key Passes", "value": playerstat.passes_key },
            { 
                "title": "Pass Accuracy", 
                "value": playerstat.passes_accuracy,
                "per_ninety": False,
                "pct": True,
            },
            { "title": "Successful Dribble", "value": playerstat.dribbles_succeeded },
            { "title": "Attempted Dribbles", "value": playerstat.dribbles_attempted },
            { 
                "title": "Dribble Success Rate", 
                "value": playerstat.dribbles_succeeded_pct,
                "per_ninety": False,
                "pct": True,
            },
            { "title": "Fouls Drawn", "value": playerstat.fouls_drawn },
            { "title": "Penalties Drawn", "value": playerstat.penalties_won },
        ]
    )
    defensive_card = Card.from_list(
        title="Defense",
        per_ninety=per_ninety,
        minutes_played=playerstat.minutes_played,
        stats=[
            { "title": "Blocks", "value": playerstat.blocks },
            { "title": "Tackles", "value": playerstat.tackles },
            { "title": "Interceptions", "value": playerstat.interceptions },
            { "title": "Successful Duels", "value": playerstat.duels_won },
            { "title": "Attempted Duels", "value": playerstat.duels },
            { 
                "title": "Duel Success Rate", 
                "value": playerstat.duels_won_pct,
                "per_ninety": False,
                "pct": True,
            },
        ]
    )
    gameplay_card = Card.from_list(
        title="Gameplay",
        per_ninety=per_ninety,
        minutes_played=playerstat.minutes_played,
        stats=[
            { "title": "Minutes Played", "value": playerstat.minutes_played, "per_ninety": False },
            { "title": "Appearances", "value": playerstat.appearances, "per_ninety": False },
            { "title": "Starts", "value": playerstat.starts, "per_ninety": False },
            { "title": "Benches", "value": playerstat.benches, "per_ninety": False },
            { "title": "Substitutions In", "value": playerstat.substitutions_in, "per_ninety": False },
            { "title": "Substitutions Out", "value": playerstat.substitutions_out, "per_ninety": False },
        ]
    )
    fouling_card = Card.from_list(
        title="Fouling",
        per_ninety=per_ninety,
        minutes_played=playerstat.minutes_played,
        stats=[
            { "title": "Yellow Cards", "value": playerstat.yellows, "per_ninety": False },
            { "title": "Red Cards", "value": playerstat.reds, "per_ninety": False },
            { "title": "Fouls Committed", "value": playerstat.fouls_committed },
            { "title": "Penalties Committed", "value": playerstat.penalties_committed },

        ]
    )
    goalkeeping_card = Card.from_list(
        title="Goalkeeping",
        per_ninety=per_ninety,
        minutes_played=playerstat.minutes_played,
        stats=[
            { "title": "Goals Conceded", "value": playerstat.goals_conceded },
            { "title": "Goals Saved", "value": playerstat.goals_saved },
            { "title": "Penalties Saved", "value": playerstat.penalties_saved, "per_ninety": False },
        ]
    )
    player_data["stats"] = CardList([
        attacking_card, 
        creation_card, 
        defensive_card, 
        gameplay_card, 
        fouling_card, 
        goalkeeping_card
    ])

    return player_data 
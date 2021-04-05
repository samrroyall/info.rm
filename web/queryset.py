from django.db.models import F, FloatField, IntegerField, Q, QuerySet, Max
from django.db.models.functions import Cast 
from typing import Callable, Dict, List, Union

from .models import Season, League, PlayerStat

def get_max( queryset: QuerySet, field: str ) -> QuerySet:
    return float( list(queryset.aggregate( Max(field) ).values())[0] )

def annotate_queryset(
    queryset: QuerySet,
    field_value: Union[FloatField, IntegerField],
    per_ninety: bool,
    annotation_name: Union[str, None] = None,
    field_name: str = ""
) -> QuerySet:
    per_ninety_value = Cast(F("minutes_played")/90.0, FloatField())
    annotation_value = field_value/per_ninety_value if per_ninety is True else field_value
    if annotation_name is None:
        annotation_name = f"{field_name}{'Per90' if per_ninety is True else ''}"
    return queryset.annotate(**{annotation_name: Cast(annotation_value, FloatField())}), annotation_name

def order_queryset(
    queryset: QuerySet, 
    field_value: Union[str, IntegerField, FloatField],
    per_ninety: bool,
    desc: bool = True,
    limit: int = 50
) -> QuerySet:
    annotated_queryset, _ = annotate_queryset(
        queryset=queryset, 
        field_value=Cast(F(field_value), FloatField()) if type(field_value) == str else field_value,
        per_ninety=per_ninety,
        annotation_name="order_field"
    )
    # may need to filter queryset more for per90 cards
    return annotated_queryset.order_by("-order_field" if desc is True else "order_field")[:limit]

def filter_by_comparison(
    queryset: QuerySet, 
    data: Dict[str, Union[int, float]], 
    field: str,
    logical_op: str = "logicalOp",
    first_val: str = "firstVal",
    second_val: str = "secondVal",
) -> QuerySet:
    field_lt = field + "__lt"
    field_gt = field + "__gt"
    if data[logical_op] == "><":
        queryset = queryset.filter( Q(**{ field_gt: float(data[first_val]) }) ) 
        queryset = queryset.filter( Q(**{ field_lt: float(data[second_val]) }) )
    elif data[logical_op] == "<":
        queryset = queryset.filter( Q(**{ field_lt: float(data[first_val]) }) )
    elif data[logical_op] == ">":
        queryset = queryset.filter( Q(**{ field_gt: float(data[first_val]) }) )
    return queryset


def modify_queryset( 
    queryset: QuerySet, 
    lambdas: List[Callable] 
) -> QuerySet:
    for l in lambdas:
        queryset = l(queryset)
    return queryset
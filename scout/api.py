from django.core.exceptions import ValidationError
from django.db import IntegrityError
from django.shortcuts import get_object_or_404
from ninja.errors import HttpError
from ninja import NinjaAPI
from .models import  Team, Player, Match, Set, Lineup, Substitution, Touch
from .schemas import (
    SetSchema, SetCreateSchema, 
    TeamSchema, TeamCreateSchema,  
    PlayerSchema, PlayerCreateSchema, 
    MatchSchema, MatchCreateSchema, 
    LineupSchema, LineupCreateSchema, 
    SubstitutionSchema, SubstitutionCreateSchema, 
    TouchSchema, TouchCreateSchema
)
api = NinjaAPI()

@api.get("/test")
def test(request):
    return{"messaggio": "API funziona"}

@api.get("/teams", response=list[TeamSchema])
def list_teams(request):
    return Team.objects.all()

@api.post("/teams", response=TeamSchema)
def create_team(request, data: TeamCreateSchema):
    team = Team.objects.create(name=data.name)
    return team

@api.get("/players", response=list[PlayerSchema])
def get_players(request):
    return Player.objects.all()

@api.get("/players/{player_id}", response=PlayerSchema)
def get_player(request, player_id: int):
    return get_object_or_404(Player, id=player_id)

@api.post("/players", response=PlayerSchema)
def create_player(request, data: PlayerCreateSchema):
    player = Player.objects.create(
        name=data.name,
        number=data.number,
        team_id=data.team_id,
    )
    return player

@api.get("/matches", response=list[MatchSchema])
def get_matches(request):
    return Match.objects.all()

@api.get("/matches/{match_id}", response=MatchSchema)
def get_match(request, match_id: int):
    return get_object_or_404(Match, id=match_id)

@api.post("/matches", response=MatchSchema)
def create_match(request, data: MatchCreateSchema):
    match = Match.objects.create(
        team_id=data.team_id,
        opponent=data.opponent,
        date=data.date,
        mode=data.mode
    )
    return match    

@api.get("/sets", response=list[SetSchema])
def get_sets(request):
    return Set.objects.all()

@api.get("/sets/{set_id}", response=SetSchema)
def get_set(request, set_id: int):
    return get_object_or_404(Set, id=set_id)

@api.post("/sets", response=SetSchema)
def create_set(request, data: SetCreateSchema):
    new_set = Set.objects.create(
        match_id=data.match_id,
        number=data.number,
    )

    return new_set

@api.post("/sets/{set_id}/initialize", response=SetSchema)
def initialize_set(request, set_id: int):
    current_set = get_object_or_404(Set, id=set_id)

    if current_set.is_initialized():
        raise HttpError(
            400,
            "Questo set è già stato inizializzato."
        )

    try:
        lineup = current_set.lineup
    except Lineup.DoesNotExist:
        raise HttpError(
            400,
            "Il set non ha ancora una formazione iniziale."
        )

    current_set.current_position_1_id = lineup.position_1_id
    current_set.current_position_2_id = lineup.position_2_id
    current_set.current_position_3_id = lineup.position_3_id
    current_set.current_position_4_id = lineup.position_4_id
    current_set.current_position_5_id = lineup.position_5_id
    current_set.current_position_6_id = lineup.position_6_id

    current_set.save()

    return current_set

@api.get("/lineups", response=list[LineupSchema])
def get_lineups(request):
    return Lineup.objects.all()

@api.post("/lineups", response=LineupSchema)
def create_lineup(request, data: LineupCreateSchema):
    lineup = Lineup(
        set_id=data.set_id,
        position_1_id=data.position_1,
        position_2_id=data.position_2,
        position_3_id=data.position_3,
        position_4_id=data.position_4,
        position_5_id=data.position_5,
        position_6_id=data.position_6,
    )

    try:
        lineup.full_clean()
        lineup.save()
    except ValidationError as e:
        messages = []

        for errors in e.message_dict.values():
            messages.extend(errors)

        raise HttpError(400, " ".join(messages))

    except IntegrityError:
        raise HttpError(
            400,
            "Questo set ha già una formazione iniziale."
        )

    return lineup

@api.get("/substitutions", response=list[SubstitutionSchema])
def get_substitutions(request):
    return Substitution.objects.all()

@api.post("/substitutions", response=SubstitutionSchema)
def create_substitution(request, data: SubstitutionCreateSchema):
    current_set = get_object_or_404(Set, id=data.set_id)

    if not current_set.is_initialized():
        raise HttpError(
            400,
            "Il set non è ancora stato inizializzato."
        )

    if data.position < 1 or data.position > 6:
        raise HttpError(
            400,
            "La posizione deve essere compresa tra 1 e 6."
        )

    current_player_id = getattr(
        current_set,
        f"current_position_{data.position}_id"
    )

    if current_player_id != data.player_out:
        raise HttpError(
            400,
            "Il giocatore indicato come uscente non occupa la posizione selezionata."
        )

    current_players = [
    current_set.current_position_1_id,
    current_set.current_position_2_id,
    current_set.current_position_3_id,
    current_set.current_position_4_id,
    current_set.current_position_5_id,
    current_set.current_position_6_id,
]

    if data.player_in in current_players:
        raise HttpError(
            400,
            "Il giocatore entrante è già presente in campo."
        )

    substitution = Substitution(
        set_id=data.set_id,
        player_out_id=data.player_out,
        player_in_id=data.player_in,
        position=data.position,
    )

    setattr(
        current_set,
        f"current_position_{data.position}_id",
        data.player_in
    )

    substitution.save()
    current_set.save()

    return substitution

@api.get("/touches", response=list[TouchSchema])
def get_touches(request):
    return Touch.objects.all()

@api.post("/touches", response=TouchSchema)
def create_touch(request, data: TouchCreateSchema):
    touch = Touch(
        match_id=data.match_id,
        set_id=data.set_id,
        player_id=data.player_id,
        fundamental=data.fundamental,
        outcome=data.outcome,
        quality=data.quality,
    )

    try:
        touch.full_clean()
    except ValidationError as e:
        messages = []

        for errors in e.message_dict.values():
            messages.extend(errors)

        raise HttpError(400, " ".join(messages))

    touch.save()

    return touch
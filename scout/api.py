from django.core.exceptions import ValidationError
from django.shortcuts import get_object_or_404
from ninja.errors import HttpError
from ninja import NinjaAPI
from .models import Team, Player, Match, Set, Touch
from .schemas import SetSchema, SetCreateSchema, TeamSchema, TeamCreateSchema,  PlayerSchema, PlayerCreateSchema, MatchSchema, MatchCreateSchema, TouchSchema, TouchCreateSchema

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
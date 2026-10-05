from ninja import NinjaAPI
from .models import Team, Player, Match, Set, Touch
from .schemas import TeamSchema, TeamCreateSchema, MatchSchema, MatchCreateSchema

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

@api.get("/matches", response=list[MatchSchema])
def get_matches(request):
    return Match.objects.all()

@api.post("/matches", response=MatchSchema)
def create_match(request, data: MatchCreateSchema):
    match = Match.objects.create(
        team_id=data.team_id,
        opponent=data.opponent,
        date=data.date,
        mode=data.mode
    )
    return match    

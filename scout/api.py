from django.core.exceptions import ValidationError
from django.db import IntegrityError, transaction
from django.shortcuts import get_object_or_404
from ninja.errors import HttpError
from ninja import NinjaAPI
from .models import  Team, Player, Match, Set, SetAction, Lineup, Substitution, Touch
from .schemas import (
    SetSchema, SetCreateSchema, ScorePointSchema,
    TeamSchema, TeamCreateSchema,  
    PlayerSchema, PlayerCreateSchema, 
    MatchSchema, MatchCreateSchema, 
    LineupSchema, LineupCreateSchema, 
    SubstitutionSchema, SubstitutionCreateSchema, 
    TouchSchema, TouchCreateSchema
)
api = NinjaAPI()


def get_set_state_snapshot(current_set):
    return {
        "our_score": current_set.our_score,
        "opponent_score": current_set.opponent_score,
        "serving_team": current_set.serving_team,
        "current_position_1_id": current_set.current_position_1_id,
        "current_position_2_id": current_set.current_position_2_id,
        "current_position_3_id": current_set.current_position_3_id,
        "current_position_4_id": current_set.current_position_4_id,
        "current_position_5_id": current_set.current_position_5_id,
        "current_position_6_id": current_set.current_position_6_id,
    }


def apply_rally_point(current_set, scoring_team):
    if scoring_team not in [Set.OUR, Set.OPPONENT]:
        raise HttpError(
            400,
            "La squadra che ha conquistato il punto deve essere OUR oppure OPPONENT."
        )

    if scoring_team == Set.OUR and current_set.serving_team == Set.OPPONENT:
        if not current_set.is_initialized():
            raise HttpError(
                400,
                "Il set deve essere inizializzato prima di ruotare i giocatori."
            )

    if scoring_team == Set.OUR:
        current_set.our_score += 1
    else:
        current_set.opponent_score += 1

    if current_set.serving_team != scoring_team:
        current_set.serving_team = scoring_team

        if scoring_team == Set.OUR:
            old_positions = [
                current_set.current_position_1_id,
                current_set.current_position_2_id,
                current_set.current_position_3_id,
                current_set.current_position_4_id,
                current_set.current_position_5_id,
                current_set.current_position_6_id,
            ]
            rotated_positions = old_positions[1:] + old_positions[:1]

            for position, player_id in enumerate(rotated_positions, start=1):
                setattr(
                    current_set,
                    f"current_position_{position}_id",
                    player_id,
                )

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

@api.post("/sets/{set_id}/point", response=SetSchema)
def record_set_point(request, set_id: int, data: ScorePointSchema):
    current_set = get_object_or_404(Set, id=set_id)

    with transaction.atomic():
        SetAction.objects.create(
            set=current_set,
            action_type=SetAction.POINT,
            before_state=get_set_state_snapshot(current_set),
        )
        apply_rally_point(current_set, data.scoring_team)
        current_set.save()
    return current_set


@api.post("/sets/{set_id}/undo", response=SetSchema)
def undo_last_set_action(request, set_id: int):
    current_set = get_object_or_404(Set, id=set_id)
    last_action = current_set.actions.order_by("-created_at", "-id").first()

    if last_action is None:
        raise HttpError(
            400,
            "Non ci sono azioni da annullare in questo set."
        )

    if last_action.action_type not in [
        SetAction.POINT,
        SetAction.SUBSTITUTION,
        SetAction.TOUCH,
    ]:
        raise HttpError(
            400,
            "Questo tipo di azione non può essere annullato."
        )

    with transaction.atomic():
        if last_action.action_type == SetAction.SUBSTITUTION:
            Substitution.objects.filter(
                id=last_action.related_id,
                set=current_set,
            ).delete()
        elif last_action.action_type == SetAction.TOUCH:
            Touch.objects.filter(
                id=last_action.related_id,
                set=current_set,
            ).delete()

        for field, value in last_action.before_state.items():
            setattr(current_set, field, value)

        current_set.save()
        last_action.delete()

    return current_set

@api.post("/sets", response=SetSchema)
def create_set(request, data: SetCreateSchema):
    if data.serving_team not in [Set.OUR, Set.OPPONENT]:
        raise HttpError(
            400,
            "La squadra al servizio deve essere OUR oppure OPPONENT."
        )

    new_set = Set.objects.create(
        match_id=data.match_id,
        number=data.number,
        serving_team=data.serving_team,
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

    match_team_id = current_set.match.team_id

    player_in = get_object_or_404(
        Player,
        id=data.player_in
    )

    if player_in.team_id != match_team_id:
        raise HttpError(
            400,
            "Il giocatore entrante non appartiene alla squadra della partita."
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

    before_state = get_set_state_snapshot(current_set)

    with transaction.atomic():
        substitution.save()
        current_set.save()
        SetAction.objects.create(
            set=current_set,
            action_type=SetAction.SUBSTITUTION,
            related_id=substitution.id,
            before_state=before_state,
        )

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

    current_set = get_object_or_404(Set, id=data.set_id)
    before_state = get_set_state_snapshot(current_set)

    with transaction.atomic():
        touch.save()
        SetAction.objects.create(
            set=current_set,
            action_type=SetAction.TOUCH,
            related_id=touch.id,
            before_state=before_state,
        )

        if touch.match.mode == Match.BASIC:
            if touch.outcome == Touch.POINT:
                apply_rally_point(current_set, Set.OUR)
            elif touch.outcome == Touch.ERROR:
                apply_rally_point(current_set, Set.OPPONENT)

        current_set.save()

    return touch

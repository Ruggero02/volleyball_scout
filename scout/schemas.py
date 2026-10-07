from ninja import Schema
from datetime import date


class TeamSchema(Schema):
    id: int
    name: str

class TeamCreateSchema(Schema):
    name: str

class PlayerSchema(Schema):
    id: int
    name: str
    number: int
    team_id: int


class PlayerCreateSchema(Schema):
    name: str
    number: int
    team_id: int

class MatchSchema(Schema):
    id: int
    team_id: int
    opponent: str
    date: date
    mode: str

class MatchCreateSchema(Schema):
    team_id: int
    opponent: str
    date: date
    mode: str

class SetSchema(Schema):
    id: int
    match_id: int
    number: int
    our_score: int
    opponent_score: int
    serving_team: str
    current_position_1_id: int | None
    current_position_2_id: int | None
    current_position_3_id: int | None
    current_position_4_id: int | None
    current_position_5_id: int | None
    current_position_6_id: int | None


class SetCreateSchema(Schema):
    match_id: int
    number: int

class TouchSchema(Schema):
    id: int
    match_id: int
    set_id: int
    player_id: int
    fundamental: str
    outcome: str | None = None
    quality: str | None = None

class TouchCreateSchema(Schema):
    match_id: int
    set_id: int
    player_id: int
    fundamental: str
    outcome: str | None = None
    quality: str | None = None

class LineupSchema(Schema):
    id: int
    set_id: int
    position_1_id: int
    position_2_id: int
    position_3_id: int
    position_4_id: int
    position_5_id: int
    position_6_id: int

class LineupCreateSchema(Schema):


    set_id: int
    position_1: int
    position_2: int
    position_3: int
    position_4: int
    position_5: int
    position_6: int

class SubstitutionSchema(Schema):
    id: int
    set_id: int
    player_out_id: int
    player_in_id: int
    position: int

class SubstitutionCreateSchema(Schema):
    set_id: int
    player_out: int
    player_in: int
    position: int
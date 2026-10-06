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
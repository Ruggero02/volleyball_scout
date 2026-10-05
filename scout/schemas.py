from ninja import Schema
from datetime import date


class TeamSchema(Schema):
    id: int
    name: str

class TeamCreateSchema(Schema):
    name: str

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


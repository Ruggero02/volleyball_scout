from django.db import models
from django.core.exceptions import ValidationError

class Team(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

class Player(models.Model):
    name = models.CharField(max_length=100)
    number = models.PositiveIntegerField()
    team = models.ForeignKey(Team, related_name='players', on_delete=models.CASCADE)

    def __str__(self):
        return f"#{self.number} {self.name}"

class Match(models.Model):
    BASIC = "BASIC"
    ADVANCED = "ADVANCED"

    MODE_CHOICES = [
        (BASIC, "Basic"),
        (ADVANCED, "Advanced"),
    ]

    team = models.ForeignKey(
        Team,
        related_name='matches',
        on_delete=models.CASCADE
    )
    opponent = models.CharField(max_length=100)
    date = models.DateField()
    mode = models.CharField(
        max_length=20,
        choices=MODE_CHOICES
    )

    def __str__(self):
        return f"{self.team} vs {self.opponent} - {self.date}"
    

class Set(models.Model):
    OUR = "OUR"
    OPPONENT = "OPPONENT"
    SERVING_TEAM_CHOICES = [
        (OUR, "Noi"),  
        (OPPONENT, "Avversari"),
    ]
    match = models.ForeignKey(
        Match,
        related_name='sets',
        on_delete=models.CASCADE
    )
    number = models.PositiveIntegerField()

    our_score = models.PositiveIntegerField(default=0)
    opponent_score = models.PositiveIntegerField(default=0)

    serving_team = models.CharField(
        max_length=10,
        choices=SERVING_TEAM_CHOICES
    )

    current_position_1 = models.ForeignKey(
        Player,
        related_name="sets_position_1",
        on_delete=models.PROTECT,
        null=True,
        blank=True
    )

    current_position_2 = models.ForeignKey(
        Player,
        related_name="sets_position_2",
        on_delete=models.PROTECT,
        null=True,
        blank=True
    )

    current_position_3 = models.ForeignKey(
        Player,
        related_name="sets_position_3",
        on_delete=models.PROTECT,
        null=True,
        blank=True
    )

    current_position_4 = models.ForeignKey(
        Player,
        related_name="sets_position_4",
        on_delete=models.PROTECT,
        null=True,
        blank=True
    )

    current_position_5 = models.ForeignKey(
        Player,
        related_name="sets_position_5",
        on_delete=models.PROTECT,
        null=True,
        blank=True
    )

    current_position_6 = models.ForeignKey(
        Player,
        related_name="sets_position_6",
        on_delete=models.PROTECT,
        null=True,
        blank=True
    )
    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["match", "number"],
                name="unique_set_per_match"
            )
        ]
        
    def __str__(self):
        return f"Set {self.number} - {self.match}"

    def is_initialized(self):
        return all([
            self.current_position_1_id,
            self.current_position_2_id,
            self.current_position_3_id,
            self.current_position_4_id,
            self.current_position_5_id,
            self.current_position_6_id,
        ])
class Lineup(models.Model):
    set = models.OneToOneField(
        Set,
        related_name="lineup",
        on_delete=models.CASCADE
    )

    position_1 = models.ForeignKey(
        Player,
        related_name="lineups_position_1",
        on_delete=models.PROTECT
    )

    position_2 = models.ForeignKey(
        Player,
        related_name="lineups_position_2",
        on_delete=models.PROTECT
    )

    position_3 = models.ForeignKey(
        Player,
        related_name="lineups_position_3",
        on_delete=models.PROTECT
    )

    position_4 = models.ForeignKey(
        Player,
        related_name="lineups_position_4",
        on_delete=models.PROTECT
    )

    position_5 = models.ForeignKey(
        Player,
        related_name="lineups_position_5",
        on_delete=models.PROTECT
    )

    position_6 = models.ForeignKey(
        Player,
        related_name="lineups_position_6",
        on_delete=models.PROTECT
    )

    def clean(self):
        players = [
            self.position_1,
            self.position_2,
            self.position_3,
            self.position_4,
            self.position_5,
            self.position_6,
        ]

        player_ids = [player.id for player in players]

        if len(set(player_ids)) != 6:
            raise ValidationError(
                "Un giocatore non può occupare più di una posizione."
            )

        team_id = self.set.match.team_id

        for player in players:
            if player.team_id != team_id:
                raise ValidationError(
                    "Tutti i giocatori della formazione devono appartenere alla squadra della partita."
                )

    def __str__(self):
        return f"Formazione - {self.set}"
class Substitution(models.Model):
    set = models.ForeignKey(
        Set,
        related_name="substitutions",
        on_delete=models.CASCADE
    )

    player_out = models.ForeignKey(
        Player,
        related_name="substitutions_out",
        on_delete=models.PROTECT
    )

    player_in = models.ForeignKey(
        Player,
        related_name="substitutions_in",
        on_delete=models.PROTECT
    )

    position = models.PositiveSmallIntegerField()

    def __str__(self):
        return (
            f"{self.player_out} → {self.player_in} "
            f"(Posizione {self.position})"
        )

class Touch(models.Model):
    SERVE = "SERVE"
    RECEPTION = "RECEPTION"
    SET = "SET"
    ATTACK = "ATTACK"
    BLOCK = "BLOCK"
    DEFENSE = "DEFENSE"
    GENERAL = "GENERAL"

    FUNDAMENTAL_CHOICES = [
        (SERVE, "Servizio"),
        (RECEPTION, "Ricezione"),
        (SET, "Alzata"),
        (ATTACK, "Attacco"),
        (BLOCK, "Muro"),
        (DEFENSE, "Difesa"),
        (GENERAL, "Generale"),
    ]

    POINT = "POINT"
    OK = "OK"
    ERROR = "ERROR"

    OUTCOME_CHOICES = [
        (POINT, "Punto"),
        (OK, "Ok"),
        (ERROR, "Errore"),
    ]

    EXCELLENT = "#"
    POSITIVE = "+"
    NEUTRAL = "!"
    SPECIAL = "/"
    NEGATIVE = "-"
    ERROR_QUALITY = "="

    QUALITY_CHOICES = [
        (EXCELLENT, "#"),
        (POSITIVE, "+"),
        (NEUTRAL, "!"),
        (SPECIAL, "/"),
        (NEGATIVE, "-"),
        (ERROR_QUALITY, "="),
    ]

    # Valutazioni disponibili per ogni fondamentale
    QUALITY_BY_FUNDAMENTAL = {
        SERVE: {EXCELLENT, POSITIVE, NEUTRAL, SPECIAL, NEGATIVE, ERROR_QUALITY},
        RECEPTION: {EXCELLENT, POSITIVE, NEUTRAL, SPECIAL, NEGATIVE, ERROR_QUALITY},
        ATTACK: {EXCELLENT, POSITIVE, NEUTRAL, SPECIAL, NEGATIVE, ERROR_QUALITY},
        BLOCK: {EXCELLENT, ERROR_QUALITY},
        DEFENSE: {EXCELLENT, POSITIVE, ERROR_QUALITY},
        SET: {EXCELLENT, ERROR_QUALITY},
        GENERAL: set(),
    }

    match = models.ForeignKey(
        Match,
        related_name="touches",
        on_delete=models.CASCADE
    )

    set = models.ForeignKey(
        Set,
        related_name="touches",
        on_delete=models.CASCADE
    )

    player = models.ForeignKey(
        Player,
        related_name="touches",
        on_delete=models.CASCADE
    )

    fundamental = models.CharField(
        max_length=20,
        choices=FUNDAMENTAL_CHOICES
    )

    outcome = models.CharField(
        max_length=10,
        choices=OUTCOME_CHOICES,
        null=True,
        blank=True
    )

    quality = models.CharField(
        max_length=1,
        choices=QUALITY_CHOICES,
        null=True,
        blank=True
    )

    def clean(self):
        if self.match.mode == Match.BASIC:
            if not self.outcome:
                raise ValidationError(
                    "Una Touch BASIC deve avere un risultato."
                )

            if self.quality:
                raise ValidationError(
                    "Una Touch BASIC non può avere una valutazione avanzata."
                )

        elif self.match.mode == Match.ADVANCED:
            if not self.quality:
                raise ValidationError(
                    "Una Touch ADVANCED deve avere una valutazione."
                )

            if self.outcome:
                raise ValidationError(
                    "Una Touch ADVANCED non può avere un risultato BASIC."
                )

            allowed_qualities = self.QUALITY_BY_FUNDAMENTAL.get(
                self.fundamental,
                set()
            )

            if self.quality not in allowed_qualities:
                raise ValidationError({
                    "quality": (
                        f"La valutazione '{self.quality}' "
                        f"non è disponibile per il fondamentale selezionato."
                    )
                })

        if self.set.match_id != self.match_id:
            raise ValidationError({
                "set": "Il set selezionato appartiene a un'altra partita."
            })

        if self.player.team_id != self.match.team_id:
            raise ValidationError({
                "player": "Il giocatore selezionato non appartiene alla squadra della partita."
            })

    def __str__(self):
        return f"{self.player} - {self.fundamental}"
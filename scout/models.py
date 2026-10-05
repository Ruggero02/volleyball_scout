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
    match = models.ForeignKey(
        Match,
        related_name='sets',
        on_delete=models.CASCADE
    )
    number = models.PositiveIntegerField()

    def __str__(self):
        return f"Set {self.number} - {self.match}"
    
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
    NEGATIVE = "-"
    ERROR_QUALITY = "="

    QUALITY_CHOICES = [
        (EXCELLENT, "#"),
        (POSITIVE, "+"),
        (NEUTRAL, "!"),
        (NEGATIVE, "-"),
        (ERROR_QUALITY, "="),
    ]

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
                    "Una Touch BASIC deve avere un outcome."
                )

            if self.quality:
                raise ValidationError(
                    "Una Touch BASIC non può avere una quality."
                )

        elif self.match.mode == Match.ADVANCED:
            if not self.quality:
                raise ValidationError(
                    "Una Touch ADVANCED deve avere una quality."
                )

            if self.outcome:
                raise ValidationError(
                    "Una Touch ADVANCED non può avere un outcome."
                )
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
from django.contrib import admin
from .models import Team, Player, Match, Set, Lineup, Substitution, Touch

admin.site.register(Team)
admin.site.register(Player)
admin.site.register(Match)
admin.site.register(Set)
admin.site.register(Lineup)
admin.site.register(Substitution)
admin.site.register(Touch)

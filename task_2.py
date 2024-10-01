from django.db import models
from django.utils import timezone
from django.db import transaction
import csv
from django.http import HttpResponse

class Player(models.Model):
    player_id = models.CharField(max_length=100)
    
    
class Level(models.Model):
    title = models.CharField(max_length=100)
    order = models.IntegerField(default=0)
    
class Prize(models.Model):
    title = models.CharField()
    
class PlayerLevel(models.Model):
    player = models.ForeignKey(Player, on_delete=models.CASCADE)
    level = models.ForeignKey(Level, on_delete=models.CASCADE)
    completed = models.DateField()
    is_completed = models.BooleanField(default=False)
    score = models.PositiveIntegerField(default=0)
    
    
class LevelPrize(models.Model):
    level = models.ForeignKey(Level, on_delete=models.CASCADE)
    prize = models.ForeignKey(Prize, on_delete=models.CASCADE)
    received = models.DateTimeField(auto_now_add=True)

class PlayerLevelService:

    @staticmethod
    @transaction.atomic
    def assign_prize_to_player(player_id, level_id, prize_id):
        try:
            player_level = PlayerLevel.objects.get(player__id=player_id, level__id=level_id, is_completed=True)
        except PlayerLevel.DoesNotExist:
            raise ValueError("Player doesnt complete this level or level doesnt exists.")
        
        if LevelPrize.objects.filter(level=level_id, prize=prize_id).exists():
            raise ValueError("Prize already get.")
        
        LevelPrize.objects.create(
            level_id=level_id,
            prize_id=prize_id,
        )

        return "Successfully won the prize!"
    
    @staticmethod
    def export_player_level_data_to_csv():
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="player_levels.csv"'

        writer = csv.writer(response)
        writer.writerow(['player_id', 'level_title', 'is_completed', 'prize_title'])

        player_levels = PlayerLevel.objects.select_related('player', 'level')\
            .prefetch_related('level__levelprize')\
            .iterator()

        for player_level in player_levels:
            prize = player_level.level.levelprize_set.first()
            prize_title = prize.prize.title if prize else "No prize"
            
            writer.writerow([
                player_level.player.player_id,
                player_level.level.title,
                player_level.is_completed,
                prize_title
            ])

        return response


PlayerLevelService.assign_prize_to_player(player_id=1, level_id=1, prize_id=2)

response = PlayerLevelService.export_player_level_data_to_csv()

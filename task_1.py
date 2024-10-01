from django.db import models
from django.utils.translation import gettext_lazy as _
from django.db.models import F
from datetime import datetime

class Player(models.Model):
    player_name = models.CharField(max_length=200, unique=True)
    
    def login_event(self):
        ########  Some Login Logic Here ##########
        
        ####### Bonus Points Logic ###########
        if not PlayerLogin.objects.exists():
            PlayerLogin.objects.create(player=self)
            PlayerScore.objects.filter(id=self.id).update(score=F('score') + 15)
            
        else:
            last_login_attempt = PlayerLogin.objects.filter(player=self).first()
            
            if last_login_attempt:
                
                last_login_day = last_login_attempt.timestamp.day
                
                if last_login_day < datetime.now().day:
                    
                    PlayerScore.objects.filter(id=self.id).update(score=F('score') + 5)
        
    def game_bonus_event(self, game_difficulty):
        type_of_boost = {
            'EASY': 1,
            'MEDIUM': 2,
            'HARD': 3,
            'EXTRA HARD': 4,
        }
        
        Boost.objects.create(player=self, boost_type=type_of_boost[game_difficulty])
        
class PlayerScore(models.Model):
    player = models.ForeignKey(Player, on_delete=models.CASCADE, related_name='scores_player')
    score = models.IntegerField(default=0)
        
class PlayerLogin(models.Model):
    player = models.ForeignKey(Player, on_delete=models.CASCADE, related_name='logged_boost')
    timestamp = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        order_by = ['-timestamp']

class Boost(models.Model):
    player = models.ForeignKey(Player, on_delete=models.CASCADE, related_name='player_boost')
    
    MAX_BOOST = 4
    HIGH_BOOST = 3
    MEDIUM_BOOST = 2 
    LOW_BOOST = 1
    
    BOOST_CHOICES = (
        (MAX_BOOST, _('Max Boost')),
        (HIGH_BOOST, _('High Boost')),
        (MEDIUM_BOOST, _('Medium Boost')),
        (LOW_BOOST, _('Low Boost')),
    )
    
    boost_type = models.CharField(_('Choice'), max_length=1, choices=BOOST_CHOICES, null=True)
    granted_at = models.DateTimeField(auto_now_add=True)

    # E.g we would make boosts validity this way: low boost : 2 mins, medium boost: 5 mins, high_boost : 8 mins, max boost : 10 mins
    
    def check_expiration(self):
        validity = {
            '1': 120,
            '2': 300,
            '3': 480,
            '4': 600,
        }
        
        if self.granted_at + validity[self.boost_type] > datetime.now():
            self.delete()
            
        else:
            return 'valid'
            
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
import random
from datetime import timedelta

class Word(models.Model):
    word = models.CharField(max_length=5, unique=True, help_text="5-letter word in uppercase")
    
    def __str__(self):
        return self.word
    
    @classmethod
    def get_random_word(cls):
        words = cls.objects.all()
        if words:
            return random.choice(words)
        return None

class GameSession(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    word = models.ForeignKey(Word, on_delete=models.CASCADE)
    date_started = models.DateTimeField(auto_now_add=True)
    completed = models.BooleanField(default=False)
    won = models.BooleanField(default=False)
    guesses_used = models.IntegerField(default=0)
    
    def __str__(self):
        return f"{self.user.username} - {self.word.word} - {self.date_started.date()}"

    @classmethod
    def games_today(cls, user):
        today = timezone.now().date()
        return cls.objects.filter(
            user=user, 
            date_started__date=today
        ).count()

    @classmethod
    def get_user_points(cls, user):
        # Total games won
        return cls.objects.filter(user=user, won=True).count()
    
    @classmethod
    def get_user_streak(cls, user):
        # Consecutive days with at least one win, up to today.
        today = timezone.now().date()
        streak = 0
        delta = 0
        while True:
            day = today - timedelta(days=delta)
            if cls.objects.filter(user=user, won=True, date_started__date=day).exists():
                streak += 1
                delta += 1
            else:
                # Stop at first day without win
                break
        return streak

class Guess(models.Model):
    game_session = models.ForeignKey(GameSession, on_delete=models.CASCADE, related_name='guesses')
    guess_word = models.CharField(max_length=5)
    guess_number = models.IntegerField()
    timestamp = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.game_session.user.username} - Guess {self.guess_number}: {self.guess_word}"
    
    def get_letter_status(self):
        """Returns list of tuples (letter, status) where status is 'correct', 'wrong_position', 'not_in_word'"""
        target_word = self.game_session.word.word
        guess_word = self.guess_word
        result = []
        
        # Count occurrences of each letter in target word
        target_counts = {}
        for letter in target_word:
            target_counts[letter] = target_counts.get(letter, 0) + 1
        
        # First pass: mark correct positions
        status_list = [''] * 5
        temp_counts = target_counts.copy()
        
        for i, letter in enumerate(guess_word):
            if letter == target_word[i]:
                status_list[i] = 'correct'
                temp_counts[letter] -= 1
        
        # Second pass: mark wrong positions and not in word
        for i, letter in enumerate(guess_word):
            if status_list[i] == '':  # Not already marked as correct
                if letter in temp_counts and temp_counts[letter] > 0:
                    status_list[i] = 'wrong_position'
                    temp_counts[letter] -= 1
                else:
                    status_list[i] = 'not_in_word'
            
            result.append((letter, status_list[i]))
        
        return result
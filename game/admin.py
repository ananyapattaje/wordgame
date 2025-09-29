from django.contrib import admin

# Register your models here.
from .models import Word, GameSession, Guess

@admin.register(Word)
class WordAdmin(admin.ModelAdmin):
    list_display = ['word']
    search_fields = ['word']

@admin.register(GameSession)
class GameSessionAdmin(admin.ModelAdmin):
    list_display = ['user', 'word', 'date_started', 'completed', 'won', 'guesses_used']
    list_filter = ['completed', 'won', 'date_started']
    search_fields = ['user__username', 'word__word']

@admin.register(Guess)
class GuessAdmin(admin.ModelAdmin):
    list_display = ['game_session', 'guess_word', 'guess_number', 'timestamp']
    list_filter = ['timestamp']
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.utils import timezone
from django.db.models import Count, Q
from .models import Word, GameSession, Guess
from .forms import CustomUserCreationForm, GuessForm, DateReportForm, UserReportForm
from .models import GameSession, Word, Guess
from .forms import GuessForm
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect

def register(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Registration successful!')
            return redirect('game')
    else:
        form = CustomUserCreationForm()
    return render(request, 'registration/register.html', {'form': form})

@login_required
def game_view(request):
    user = request.user
    games_today = GameSession.games_today(user)
    today = timezone.now().date()
    games_today_count = GameSession.objects.filter(
        user=request.user,
        completed=True,
        date_started__date=today
    ).count()

    # Calculate points and streak for user
    points = GameSession.get_user_points(user)
    streak = GameSession.get_user_streak(user)

    # Always provide games_today, points, streak in context
    if games_today_count >= 3:
        messages.warning(request, 'You have reached your daily limit of 3 games. Come back tomorrow!')
        return render(request, 'game/game.html', {
            'daily_limit_reached': True,
            'games_today': games_today_count,
            'points': points,
            'streak': streak,
        })

    # Get or create current game session
    current_game = GameSession.objects.filter(
        user=request.user,
        completed=False
    ).first()

    if not current_game:
        random_word = Word.get_random_word()
        if not random_word:
            messages.error(request, 'No words available. Please contact admin.')
            return render(request, 'game/game.html', {
                'no_words': True,
                'games_today': games_today_count,
                'points': points,
                'streak': streak,
            })

        current_game = GameSession.objects.create(
            user=request.user,
            word=random_word
        )

    guesses = current_game.guesses.all().order_by('guess_number')
    remaining_guesses = 5 - guesses.count()

    if request.method == 'POST':
        form = GuessForm(request.POST)
        if form.is_valid() and not current_game.completed:
            guess_word = form.cleaned_data['guess']
            guess_number = guesses.count() + 1

            # Create guess
            guess = Guess.objects.create(
                game_session=current_game,
                guess_word=guess_word,
                guess_number=guess_number
            )

            # Check if guess is correct
            if guess_word == current_game.word.word:
                current_game.completed = True
                current_game.won = True
                current_game.guesses_used = guess_number
                current_game.save()
                messages.success(request, 'Congratulations! You guessed the word correctly!')
                # Update points and streak after win
                points = GameSession.get_user_points(user)
                streak = GameSession.get_user_streak(user)
                return render(request, 'game/game.html', {
                    'current_game': current_game,
                    'guesses': current_game.guesses.all().order_by('guess_number'),
                    'game_won': True,
                    'games_today': games_today_count,
                    'points': points,
                    'streak': streak,
                })
            elif guess_number >= 5:
                current_game.completed = True
                current_game.won = False
                current_game.guesses_used = guess_number
                current_game.save()
                messages.info(request, f'Better luck next time! The word was: {current_game.word.word}')
                # Update streak/points as a loss may break streak next day
                points = GameSession.get_user_points(user)
                streak = GameSession.get_user_streak(user)
                return render(request, 'game/game.html', {
                    'current_game': current_game,
                    'guesses': current_game.guesses.all().order_by('guess_number'),
                    'game_lost': True,
                    'games_today': games_today_count,
                    'points': points,
                    'streak': streak,
                })
            else:
                return redirect('game')
    else:
        form = GuessForm()

    return render(request, 'game/game.html', {
        'form': form,
        'current_game': current_game,
        'guesses': guesses,
        'remaining_guesses': remaining_guesses,
        'remaining_guesses_range': range(remaining_guesses),
        'games_today': games_today_count,
        'points': points,
        'streak': streak,
    })

def is_admin(user):
    return user.is_staff

@login_required
@user_passes_test(is_admin)
def reports_view(request):
    return render(request, 'game/reports.html')

@login_required
@user_passes_test(is_admin)
def daily_report(request):
    if request.method == 'POST':
        form = DateReportForm(request.POST)
        if form.is_valid():
            report_date = form.cleaned_data['report_date']

            games = GameSession.objects.filter(date_started__date=report_date)
            games = games.filter(user__is_superuser=False, user__is_staff=False)

            total_users = games.values('user').distinct().count()
            correct_guesses = games.filter(won=True).count()

            context = {
                'form': form,
                'report_date': report_date,
                'total_users': total_users,
                'correct_guesses': correct_guesses,
                'total_games': games.count(),
            }
            return render(request, 'game/daily_report.html', context)
    else:
        form = DateReportForm(initial={'report_date': timezone.now().date()})

    return render(request, 'game/daily_report.html', {'form': form})

@login_required
@user_passes_test(is_admin)
def user_report(request):
    if request.method == 'POST':
        form = UserReportForm(request.POST)
        if form.is_valid():
            selected_user = form.cleaned_data['user']

            games = GameSession.objects.filter(user=selected_user).order_by('-date_started')

            from collections import defaultdict
            daily_stats = defaultdict(lambda: {'games': 0, 'wins': 0})

            for game in games:
                date = game.date_started.date()
                daily_stats[date]['games'] += 1
                if game.won:
                    daily_stats[date]['wins'] += 1

            context = {
                'form': form,
                'selected_user': selected_user,
                'daily_stats': dict(daily_stats),
                'total_games': games.count(),
                'total_wins': games.filter(won=True).count(),
            }
            return render(request, 'game/user_report.html', context)
    else:
        form = UserReportForm()

    return render(request, 'game/user_report.html', {'form': form})

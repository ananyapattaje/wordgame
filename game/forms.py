from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
import re
from nltk.corpus import words
import pandas as pd

# Load only once when the file is imported
WORD_SET = set(pd.read_csv("C:/Users/anany/combined_words.csv")['word'].str.upper())

def is_valid_word(word):
    return word in WORD_SET

class CustomUserCreationForm(UserCreationForm):
    username = forms.CharField(
        max_length=150,
        help_text='Username must be at least 5 characters with both upper and lower case letters.',
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter username'
        })
    )
    password1 = forms.CharField(
        label='Password',
        help_text='Password must be at least 5 characters long and include alphabetic, numeric, and special characters ($, %, *, @).',
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter password'
        })
    )
    password2 = forms.CharField(
        label='Confirm Password',
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Confirm password'
        })
    )
   
    class Meta:
        model = User
        fields = ("username", "password1", "password2")
    
    def clean_username(self):
        username = self.cleaned_data.get('username')
        if len(username) < 5:
            raise ValidationError('Username must be at least 5 characters long.')
        
        if not (any(c.isupper() for c in username) and any(c.islower() for c in username)):
            raise ValidationError('Username must contain both upper and lower case letters.')
        
        return username
    
    def clean_password1(self):
        password = self.cleaned_data.get('password1')
        if len(password) < 5:
            raise ValidationError('Password must be at least 5 characters long.')
        
        if not re.search(r'[a-zA-Z]', password):
            raise ValidationError('Password must contain alphabetic characters.')
        
        if not re.search(r'\d', password):
            raise ValidationError('Password must contain numeric characters.')
        
        if not re.search(r'[$%*@]', password):
            raise ValidationError('Password must contain at least one special character ($, %, *, @).')
        
        return password

class GuessForm(forms.Form):
    guess = forms.CharField(
        max_length=5,
        min_length=5,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter 5-letter word',
            'style': 'text-transform: uppercase;'
        })
    )
    
    def clean_guess(self):
        guess = self.cleaned_data.get('guess')
        if guess:
            guess = guess.upper()
            if not guess.isalpha():
                raise ValidationError('Guess must contain only letters.')
            if len(guess) != 5:
                raise ValidationError('Guess must be exactly 5 letters.')
            if not is_valid_word(guess):
                raise ValidationError('Guess must be a valid English word.')
        return guess

class DateReportForm(forms.Form):
    report_date = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'})
    )

class UserReportForm(forms.Form):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['user'] = forms.ModelChoiceField(
            queryset=User.objects.filter(is_staff=False, is_superuser=False),
            widget=forms.Select(attrs={'class': 'form-select'})
        )
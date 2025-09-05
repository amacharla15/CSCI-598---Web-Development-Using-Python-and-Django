from django import forms
from django.core import validators
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib.auth.models import User

def validate_square(value):
    """
    Validator for a chess square.
    Expects a 2-character string like "e2": file in a-h and rank in 1-8.
    """
    if len(value) != 2:
        raise forms.ValidationError("Enter a square in the format e2.")
    file = value[0].lower()
    rank = value[1]
    if file not in "abcdefgh":
        raise forms.ValidationError("File must be a letter from a to h.")
    if not rank.isdigit() or not (1 <= int(rank) <= 8):
        raise forms.ValidationError("Rank must be a number from 1 to 8.")

class ChessForm(forms.Form):
    source = forms.CharField(
        min_length=2, max_length=2, strip=True,
        widget=forms.TextInput(attrs={'placeholder': 'e2'}),
        validators=[validators.MinLengthValidator(2),
                    validators.MaxLengthValidator(2),
                    validate_square]
    )
    destination = forms.CharField(
        min_length=2, max_length=2, strip=True,
        widget=forms.TextInput(attrs={'placeholder': 'e4'}),
        validators=[validators.MinLengthValidator(2),
                    validators.MaxLengthValidator(2),
                    validate_square]
    )

class JoinForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput(attrs={'autocomplete': 'new-password'}))
    email = forms.CharField(widget=forms.TextInput(attrs={'size': '30'}))
    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'username', 'email', 'password')
        help_texts = {'username': None}

class LoginForm(forms.Form):
    username = forms.CharField()
    password = forms.CharField(widget=forms.PasswordInput())

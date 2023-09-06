from django import forms
from django.forms.models import ModelForm

from .models import Question


class QuestionForm(ModelForm):
    """Форма вопроса"""
    text = forms.CharField(widget=forms.TextInput(attrs={'style': "background-color: rgba(75, 0, 130, 0.1)"}))

    class Meta:
        model = Question
        fields = ['text', ]

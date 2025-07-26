from django import forms
from .models import Todo

class TodoForm(forms.ModelForm):
    class Meta:
        model = Todo
        fields = ['title', 'due_date', 'priority']
        widgets = {
            'due_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'priority': forms.Select(attrs={'class': 'form-select'}),
        }
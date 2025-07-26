from django.db import models
from django.contrib.auth.models import User
# Create your models here.

class Todo(models.Model):
    PRIORITY_CHOICES = [
        ('L', 'Low'),
        ('M', 'Medium'),
        ('H', 'High'),
    ]
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=100)
    completed = models.BooleanField(default=False)
    due_date = models.DateField(null=True, blank=True)
    priority = models.CharField(max_length=1, choices=PRIORITY_CHOICES, default='M')

    def __str__(self):
        return self.title
from django.db import models
from django.contrib.auth.models import User

class Board(models.Model):
    title = models.CharField(max_length=50)
    owner = models.ForeignKey(User, related_name='owned_boards', on_delete=models.CASCADE)
    members = models.ManyToManyField(User, related_name='boards')

    def __str__(self):
        return self.title
    
class Task(models.Model):
    board = models.ForeignKey(Board, on_delete=models.CASCADE, related_name='tasks')
    title = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=[('to-do', 'To Do'), ('in-progress', 'In Progress'), ('review', 'Review'), ('done', 'Done')])
    priority = models.CharField(max_length=10, choices=[('low', 'Low'), ('medium', 'Medium'), ('high', 'High')])
    assignee = models.ForeignKey(User, null=True, blank=True, related_name='assigned_tasks', on_delete=models.SET_NULL)
    reviewer = models.ForeignKey(User, null=True, blank=True, related_name='reviewed_tasks', on_delete=models.SET_NULL)
    due_date = models.DateField(null=True, blank=True)

    def __str__(self):
        return self.title

    @property
    def comments_count(self):
        return 0


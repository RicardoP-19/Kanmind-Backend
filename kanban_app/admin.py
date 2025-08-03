from django.contrib import admin
from .models import Board, Task, Comment

@admin.register(Board)
class BoardAdmin(admin.ModelAdmin):
    list_display = ['id', 'title', 'owner', 'member_count']
    search_fields = ['title', 'owner__email']
    list_filter = ['owner']
    
    def member_count(self, obj):
        return obj.members.count()

@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ['id', 'title', 'board', 'status', 'priority', 'assignee', 'reviewer', 'due_date']
    search_fields = ['title', 'assignee__email', 'reviewer__email']
    list_filter = ['board', 'status', 'priority']
    date_hierarchy = 'due_date'

@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ['id', 'task', 'author', 'created_at', 'short_content']
    search_fields = ['author__email', 'content']
    list_filter = ['created_at', 'author']

    def short_content(self, obj):
        return (obj.content[:30] + '...') if len(obj.content) > 30 else obj.content
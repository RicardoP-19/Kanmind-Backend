from rest_framework import serializers
from kanban_app.models import Board

class BoardSerializer(serializers.ModelSerializer):
    member_count = serializers.SerializerMethodField()
    ticket_count = serializers.SerializerMethodField()
    tasks_to_do_count = serializers.SerializerMethodField()
    tasks_high_prio_count = serializers.SerializerMethodField()

    class Meta:
        model = Board
        fields = ['id', 'title', 'owner', 'member_count', 'ticket_count', 'tasks_to_do_count', 'tasks_high_prio_count']

    def get_member_count(self, obj):
        return obj.members.count()

    def get_ticket_count(self, obj):
        return obj.task_set.count()

    def get_tasks_to_do_count(self, obj):
        return obj.task_set.filter(status='to-do').count()

    def get_tasks_high_prio_count(self, obj):
        return obj.task_set.filter(priority='high').count()

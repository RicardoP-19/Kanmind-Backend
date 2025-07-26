from rest_framework import serializers
from kanban_app.models import Board
from django.contrib.auth.models import User

class BoardSerializer(serializers.ModelSerializer):
    owner_id = serializers.IntegerField(source='owner.id', read_only=True)
    member_count = serializers.SerializerMethodField()
    ticket_count = serializers.SerializerMethodField()
    tasks_to_do_count = serializers.SerializerMethodField()
    tasks_high_prio_count = serializers.SerializerMethodField()
    members = serializers.ListField(write_only=True, child=serializers.IntegerField(), required=False)

    class Meta:
        model = Board
        fields = [
            'id',
            'title',
            'owner_id',
            'member_count',
            'ticket_count',
            'tasks_to_do_count',
            'tasks_high_prio_count',
            'members'
        ]

    def get_member_count(self, obj):
        return obj.members.count()

    def get_ticket_count(self, obj):
        return 0

    def get_tasks_to_do_count(self, obj):
        return 0

    def get_tasks_high_prio_count(self, obj):
        return 0
    
    def create(self, validated_data):
        request = self.context.get('request')
        user = request.user

        members_ids = validated_data.pop('members', [])
        if user.id not in members_ids:
            members_ids.append(user.id)

        board = Board.objects.create(title=validated_data['title'], owner=user)
        board.members.set(User.objects.filter(id__in=members_ids))
        return board

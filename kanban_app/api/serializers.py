from rest_framework import serializers
from kanban_app.models import Board, Task
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
    
class MemberSerializer(serializers.ModelSerializer):
    fullname = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['id', 'email', 'fullname']

    def get_fullname(self, obj):
        return f"{obj.first_name} {obj.last_name}".strip()

class BoardDetailSerializer(serializers.ModelSerializer):
    owner_id = serializers.IntegerField(source='owner.id')
    members = MemberSerializer(many=True)
    tasks = serializers.SerializerMethodField()

    class Meta:
        model = Board
        fields = ['id', 'title', 'owner_id', 'members', 'tasks']

    def get_tasks(self, obj):
        return []
    
class BoardUpdateSerializer(serializers.ModelSerializer):
    members = serializers.ListField(child=serializers.IntegerField(), required=False)
    owner_data = serializers.SerializerMethodField()
    members_data = serializers.SerializerMethodField()

    class Meta:
        model = Board
        fields = ['id', 'title', 'members', 'owner_data', 'members_data']

    def update(self, instance, validated_data):
        members_ids = validated_data.pop('members', None)
        if members_ids is not None:
            instance.members.set(User.objects.filter(id__in=members_ids))
        instance.title = validated_data.get('title', instance.title)
        instance.save()
        return instance

    def get_owner_data(self, obj):
        return MemberSerializer(obj.owner).data

    def get_members_data(self, obj):
        return MemberSerializer(obj.members.all(), many=True).data
    

class TaskUserSerializer(serializers.ModelSerializer):
    fullname = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['id', 'email', 'fullname']

    def get_fullname(self, obj):
        return f"{obj.first_name} {obj.last_name}".strip()

class TaskSerializer(serializers.ModelSerializer):
    assignee = TaskUserSerializer(read_only=True)
    reviewer = TaskUserSerializer(read_only=True)

    class Meta:
        model = Task
        fields = [
            'id',
            'board',
            'title',
            'description',
            'status',
            'priority',
            'assignee',
            'reviewer',
            'due_date',
            'comments_count'
        ]


class TaskCreateSerializer(serializers.ModelSerializer):
    assignee_id = serializers.IntegerField(required=False, allow_null=True)
    reviewer_id = serializers.IntegerField(required=False, allow_null=True)

    class Meta:
        model = Task
        fields = [
            "board", "title", "description", "status", "priority",
            "assignee_id", "reviewer_id", "due_date"
        ]

    def validate(self, data):
        board = data["board"]
        user = self.context["request"].user

        if user != board.owner and user not in board.members.all():
            raise serializers.ValidationError("You are not a member of this board.")

        for field in ["assignee_id", "reviewer_id"]:
            uid = data.get(field)
            if uid is not None:
                if not board.members.filter(id=uid).exists():
                    raise serializers.ValidationError(f"User with id {uid} is not a board member.")

        return data

    def create(self, validated_data):
        assignee_id = validated_data.pop("assignee_id", None)
        reviewer_id = validated_data.pop("reviewer_id", None)

        task = Task.objects.create(**validated_data)

        if assignee_id:
            task.assignee_id = assignee_id
        if reviewer_id:
            task.reviewer_id = reviewer_id

        task.save()
        return task
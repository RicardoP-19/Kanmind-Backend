from rest_framework import serializers
from kanban_app.models import Board, Task, Comment
from django.contrib.auth import get_user_model 
User = get_user_model()

class BoardSerializer(serializers.ModelSerializer):
    """
    Serializer for creating and listing boards
    """
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
    """
    Serializer for User data used in board and task context.
    """
    fullname = serializers.SerializerMethodField()
    class Meta:
        model = User
        fields = ['id', 'email', 'fullname']

    def get_fullname(self, obj):
        return f"{obj.first_name} {obj.last_name}".strip()

class BoardDetailSerializer(serializers.ModelSerializer):
    """
    Detailed serializer for board view: includes tasks and full member info.
    """
    owner_id = serializers.IntegerField(source='owner.id')
    members = MemberSerializer(many=True)
    tasks = serializers.SerializerMethodField()
    class Meta:
        model = Board
        fields = ['id', 'title', 'owner_id', 'members', 'tasks']

    def get_tasks(self, obj):
        return []

class BoardUpdateSerializer(serializers.ModelSerializer):
    """
    Serializer for updating a board and returning full member and owner info.
    """
    members = serializers.ListField(child=serializers.IntegerField(), write_only=True, required=False)
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
    """
    Serializer for displaying assignee/reviewer user data in tasks.
    """
    fullname = serializers.SerializerMethodField()
    class Meta:
        model = User
        fields = ['id', 'email', 'fullname']

    def get_fullname(self, obj):
        return f"{obj.first_name} {obj.last_name}".strip()

class TaskSerializer(serializers.ModelSerializer):
    """
    Read-only task serializer with nested user info for assignee/reviewer.
    """
    assignee = TaskUserSerializer(read_only=True)
    reviewer = TaskUserSerializer(read_only=True)
    comments_count = serializers.SerializerMethodField()
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

    def get_comments_count(self, obj):
        return Comment.objects.filter(task=obj).count()

class TaskCreateSerializer(serializers.ModelSerializer):
    """
    Serializer for creating new tasks. Includes validation for board membership.
    """
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
    
class TaskUpdateSerializer(serializers.ModelSerializer):
    """
    Serializer for updating an existing task with permissions and checks.
    """
    assignee_id = serializers.IntegerField(required=False, allow_null=True)
    reviewer_id = serializers.IntegerField(required=False, allow_null=True)
    class Meta:
        model = Task
        fields = [
            "title", "description", "status", "priority",
            "assignee_id", "reviewer_id", "due_date"
        ]

    def validate(self, data):
        task = self.instance
        board = task.board
        user = self.context["request"].user

        if user != board.owner and user not in board.members.all():
            raise serializers.ValidationError("You are not a member of this board.")

        for field in ["assignee_id", "reviewer_id"]:
            uid = data.get(field)
            if uid is not None:
                if not board.members.filter(id=uid).exists():
                    raise serializers.ValidationError(f"User {uid} is not a board member.")
        return data

    def update(self, instance, validated_data):
        instance.title = validated_data.get("title", instance.title)
        instance.description = validated_data.get("description", instance.description)
        instance.status = validated_data.get("status", instance.status)
        instance.priority = validated_data.get("priority", instance.priority)
        instance.due_date = validated_data.get("due_date", instance.due_date)
        instance.assignee_id = validated_data.get("assignee_id") if "assignee_id" in validated_data else instance.assignee_id
        instance.reviewer_id = validated_data.get("reviewer_id") if "reviewer_id" in validated_data else instance.reviewer_id
        instance.save()
        return instance

class CommentSerializer(serializers.ModelSerializer):
    """
    Serializer for listing and creating task comments.
    """
    author = serializers.SerializerMethodField()
    class Meta:
        model = Comment
        fields = ['id', 'created_at', 'author', 'content']

    def get_author(self, obj):
        return obj.author.get_full_name()
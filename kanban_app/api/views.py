from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView, CreateAPIView, ListAPIView
from kanban_app.models import Board, Comment, Task
from .serializers import BoardSerializer, BoardDetailSerializer, BoardUpdateSerializer, TaskSerializer, TaskCreateSerializer, TaskUpdateSerializer, CommentSerializer
from django.shortcuts import get_object_or_404
from django.db.models import Q
from django.contrib.auth import get_user_model
from .permissions import IsBoardOwnerOrMember, IsBoardOwner, IsTaskBoardMember, IsCommentAuthor

User = get_user_model()
class BoardListView(ListCreateAPIView):
    """
    Lists boards the user owns or is member of.
    Allows creation of a new board.
    """
    serializer_class = BoardSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        return Board.objects.filter(Q(owner=user) | Q(members=user)).distinct()

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

class BoardDetailView(RetrieveUpdateDestroyAPIView):
    """
    Get, update or delete a specific board.
    Access limited to board owner or members.
    """
    serializer_class = BoardDetailSerializer
    permission_classes = [IsAuthenticated, IsBoardOwnerOrMember]
    lookup_url_kwarg = "board_id"

    def get_queryset(self):
        user = self.request.user
        return Board.objects.filter(Q(owner=user) | Q(members=user)).distinct()

    def get_serializer_class(self):
        if self.request.method in ['PATCH', 'PUT']:
            return BoardUpdateSerializer
        return BoardDetailSerializer

class EmailCheckView(APIView):
    """
    Checks if a user exists for the given email.
    Returns ID and full name if found.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        email = request.query_params.get('email')
        if not email:
            return Response({'error': 'Email parameter is required.'}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response({'error': 'User not found.'}, status=status.HTTP_404_NOT_FOUND)
        
        fullname = f"{user.first_name} {user.last_name}".strip()

        return Response({
            'id': user.id,
            'email': user.email,
            'fullname': fullname
        }, status=status.HTTP_200_OK)

class TasksAssignedToMeView(ListAPIView):
    """
    Returns all tasks assigned to the current user.
    """
    serializer_class = TaskSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Task.objects.filter(assignee=self.request.user)

class TasksReviewingView(ListAPIView):
    """
    Returns all tasks where the current user is reviewer.
    """
    serializer_class = TaskSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Task.objects.filter(reviewer=self.request.user)

class TaskCreateView(CreateAPIView):
    """
    Creates a new task if user has board access.
    """
    serializer_class = TaskCreateSerializer
    permission_classes = [IsAuthenticated]

    # def perform_create(self, serializer):
    #     serializer.save()
    def create(self, request, *args, **kwargs):
        ser = self.get_serializer(data=request.data, context={'request': request})
        ser.is_valid(raise_exception=True)
        task = ser.save()
        out = TaskSerializer(task).data  # <- exakt wie in der Doku
        headers = self.get_success_headers(out)
        return Response(out, status=status.HTTP_201_CREATED, headers=headers)

class TaskDetailView(RetrieveUpdateDestroyAPIView):
    """
    Update or delete a task.
    Only board owner can delete.
    """
    serializer_class = TaskUpdateSerializer
    permission_classes = [IsAuthenticated, IsTaskBoardMember]
    lookup_url_kwarg = "task_id"

    def get_queryset(self):
        user = self.request.user
        return Task.objects.filter(
            Q(board__members=user) | Q(board__owner=user)
        ).distinct()

    def get_serializer_class(self):
        if self.request.method in ['PATCH', 'PUT']:
            return TaskUpdateSerializer
        return TaskSerializer
    
    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', request.method == 'PATCH')
        instance = self.get_object()
        in_ser = self.get_serializer(instance, data=request.data, partial=partial, context={'request': request})
        in_ser.is_valid(raise_exception=True)
        task = in_ser.save()

        out = TaskSerializer(task).data
        out.pop("board", None)
        out.pop("comments_count", None)
        return Response(out, status=status.HTTP_200_OK)

class TaskCommentsView(APIView):
    """
    Lists or adds comments for a given task.
    Access only for board members and owner.
    Delete a comment only if the current user is the author.
    """
    permission_classes = [IsAuthenticated, IsTaskBoardMember]

    def get(self, request, task_id):
        task = get_object_or_404(Task, id=task_id)
        self.check_object_permissions(request, task)
        comments = task.comments.all().order_by('created_at')
        serializer = CommentSerializer(comments, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request, task_id):
        task = get_object_or_404(Task, id=task_id)
        self.check_object_permissions(request, task)
        serializer = CommentSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(task=task, author=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, task_id, comment_id=None):
        comment = get_object_or_404(Comment, id=comment_id, task__id=task_id)
        self.check_object_permissions(request, comment.task)
        IsCommentAuthor().has_object_permission(request, self, comment) or self.permission_denied(request, message="Not the author.")
        comment.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
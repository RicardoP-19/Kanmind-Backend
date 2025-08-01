from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from kanban_app.models import Board, Comment
from .serializers import BoardSerializer, BoardDetailSerializer, BoardUpdateSerializer, TaskSerializer, TaskCreateSerializer, TaskUpdateSerializer, CommentSerializer
from django.shortcuts import get_object_or_404
from rest_framework.exceptions import PermissionDenied
from django.db.models import Q
from django.contrib.auth import get_user_model
from kanban_app.models import Task

User = get_user_model()
class BoardListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        boards = Board.objects.filter(Q(owner=user) | Q(members=user)).distinct()
        serializer = BoardSerializer(boards, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    def post(self, request):
        serializer = BoardSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            board = serializer.save()
            return Response(BoardSerializer(board).data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
class BoardDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, board_id):
        board = get_object_or_404(Board, id=board_id)

        if request.user != board.owner and request.user not in board.members.all():
            raise PermissionDenied("You do not have access to this board.")

        serializer = BoardDetailSerializer(board)
        return Response(serializer.data)
    
    def patch(self, request, board_id):
        board = get_object_or_404(Board, id=board_id)

        if request.user != board.owner and request.user not in board.members.all():
            raise PermissionDenied("You do not have access to modify this board.")

        serializer = BoardUpdateSerializer(board, data=request.data, partial=True, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            updated_board = Board.objects.get(id=board.id)
            response_serializer = BoardDetailSerializer(updated_board)
            return Response(response_serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def delete(self, request, board_id):
        board = get_object_or_404(Board, id=board_id)

        if request.user != board.owner:
            raise PermissionDenied("Only the board owner can delete this board.")

        board.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

class EmailCheckView(APIView):
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

class TasksAssignedToMeView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        tasks = Task.objects.filter(assignee=user)
        serializer = TaskSerializer(tasks, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
class TasksReviewingView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        tasks = Task.objects.filter(reviewer=request.user)
        serializer = TaskSerializer(tasks, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class TaskCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = TaskCreateSerializer(data=request.data, context={"request": request})
        if serializer.is_valid():
            task = serializer.save()
            return Response(TaskSerializer(task).data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class TaskDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def patch(self, request, task_id):
        task = get_object_or_404(Task, id=task_id)
        board = task.board
        user = request.user

        if user != board.owner and user not in board.members.all():
            raise PermissionDenied("You are not allowed to modify this task.")

        serializer = TaskUpdateSerializer(task, data=request.data, partial=True, context={"request": request})
        if serializer.is_valid():
            updated_task = serializer.save()
            return Response(TaskSerializer(updated_task).data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, task_id):
        task = get_object_or_404(Task, id=task_id)
        board = task.board
        user = request.user

        if user != board.owner:
            raise PermissionDenied("You are not allowed to delete this task.")

        task.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class TaskCommentsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, task_id):
        task = get_object_or_404(Task, id=task_id)
        if request.user not in task.board.members.all() and request.user != task.board.owner:
            return Response({"detail": "Forbidden"}, status=status.HTTP_403_FORBIDDEN)
        comments = task.comments.all().order_by('created_at')
        serializer = CommentSerializer(comments, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    def post(self, request, task_id):
        task = get_object_or_404(Task, id=task_id)
        if request.user not in task.board.members.all() and request.user != task.board.owner:
            return Response({"detail": "Forbidden"}, status=status.HTTP_403_FORBIDDEN)

        serializer = CommentSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(task=task, author=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
class TaskCommentDeleteView(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request, task_id, comment_id):
        comment = get_object_or_404(Comment, id=comment_id, task__id=task_id)
        if comment.author != request.user:
            return Response({"detail": "Forbidden"}, status=status.HTTP_403_FORBIDDEN)
        comment.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

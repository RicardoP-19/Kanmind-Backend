from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from kanban_app.models import Board
from .serializers import BoardSerializer
from django.db.models import Q
from django.contrib.auth.models import User


class BoardListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        boards = Board.objects.filter(Q(owner=user) | Q(members=user)).distinct()
        serializer = BoardSerializer(boards, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    def post(self, request):
        user = request.user
        title = request.data.get('title')
        members = request.data.get('members', [])

        if not title:
            return Response({'error': 'Title is required.'}, status=status.HTTP_400_BAD_REQUEST)

        board = Board.objects.create(title=title, owner=user)
        print(f"Board erstellt: '{board.title}' von User-ID {user.id}")

        if user.id not in members:
            members.append(user.id)

        board.members.set(User.objects.filter(id__in=members))
        print(f"Mitglieder hinzugefügt: {members}")

        serializer = BoardSerializer(board)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


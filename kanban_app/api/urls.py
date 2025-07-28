from django.urls import path
from .views import BoardListView, BoardDetailView, EmailCheckView, TasksAssignedToMeView

urlpatterns = [
    path('boards/', BoardListView.as_view(), name='board-list'),
    path('boards/<int:board_id>/', BoardDetailView.as_view(), name='board-detail'),
    path('email-check/', EmailCheckView.as_view(), name='email-check'),
    path('tasks/assigned-to-me/', TasksAssignedToMeView.as_view(), name='tasks-assigned-to-me'),
]

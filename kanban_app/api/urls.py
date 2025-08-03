from django.urls import path
from .views import BoardListView, BoardDetailView, EmailCheckView, TasksAssignedToMeView, TasksReviewingView, TaskCreateView, TaskDetailView, TaskCommentsView

urlpatterns = [
    path('boards/', BoardListView.as_view(), name='board-list'),
    path('boards/<int:board_id>/', BoardDetailView.as_view(), name='board-detail'),
    path('email-check/', EmailCheckView.as_view(), name='email-check'),
    path('tasks/assigned-to-me/', TasksAssignedToMeView.as_view(), name='tasks-assigned-to-me'),
    path("tasks/reviewing/", TasksReviewingView.as_view(), name="tasks-reviewing"),
    path("tasks/", TaskCreateView.as_view(), name="task-create"),
    path("tasks/<int:task_id>/", TaskDetailView.as_view(), name="task-detail"),
    path('tasks/<int:task_id>/comments/', TaskCommentsView.as_view()),
    path('tasks/<int:task_id>/comments/<int:comment_id>/', TaskCommentsView.as_view()),
]

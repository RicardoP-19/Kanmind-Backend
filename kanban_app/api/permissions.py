from rest_framework.permissions import BasePermission

class IsAuthenticatedAndBoardMember(BasePermission):
    """
    Allows access only for authenticated users.
    (Note: This does not explicitly check board membership.)
    """
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated

class IsBoardOwnerOrMember(BasePermission):
    """
    Grants access if the user is either
    - the owner of the board, or
    - a member of the board.
    Typically used for board-related objects.
    """
    def has_object_permission(self, request, view, obj):
        return obj.owner == request.user or request.user in obj.members.all()

class IsBoardOwner(BasePermission):
    """
    Grants access only if the user is the owner of the board.
    Used for actions that should be restricted to board owners (e.g., deleting a board).
    """
    def has_object_permission(self, request, view, obj):
        return obj.owner == request.user

class IsTaskBoardMember(BasePermission):
    """
    Grants access if the user is either
    - the owner of the board that the task belongs to, or
    - a member of that board.
    Used for task-related actions.
    """
    def has_object_permission(self, request, view, obj):
        return obj.board.owner == request.user or request.user in obj.board.members.all()

class IsCommentAuthor(BasePermission):
    """
    Grants access only if the user is the author of the comment.
    Used for actions like deleting or editing comments.
    """
    def has_object_permission(self, request, view, obj):
        return obj.author == request.user

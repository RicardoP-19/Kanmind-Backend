from rest_framework.permissions import BasePermission

class IsAuthenticatedAndBoardMember(BasePermission):
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated

class IsBoardOwnerOrMember(BasePermission):
    def has_object_permission(self, request, view, obj):
        return obj.owner == request.user or request.user in obj.members.all()

class IsBoardOwner(BasePermission):
    def has_object_permission(self, request, view, obj):
        return obj.owner == request.user

class IsTaskBoardMember(BasePermission):
    def has_object_permission(self, request, view, obj):
        return obj.board.owner == request.user or request.user in obj.board.members.all()

class IsCommentAuthor(BasePermission):
    def has_object_permission(self, request, view, obj):
        return obj.author == request.user

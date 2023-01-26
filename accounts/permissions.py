from django.contrib.auth import get_user_model
from rest_framework.permissions import BasePermission, IsAdminUser


class IsAuthorPermission(BasePermission):
    def has_object_permission(self, request, view, obj):
        if obj.user == request.user or request.user.user_status == 'main' or 'manager' == request.user.user_status \
                or 'moderator' == request.user.user_status:
            return True
        return False


class UserIsAuthorPermission(BasePermission):
    def has_object_permission(self, request, view, obj):
        if obj.user == request.user:
            return True
        return False


class PostingUserIsAuthorPermission(BasePermission):
    def has_object_permission(self, request, view, obj):
        if obj.vacancy.user == request.user or obj.resume.user == request.user:
            return True
        return False


class PersonalIsAuthorPermission(BasePermission):
    def has_object_permission(self, request, view, obj):
        if obj.profile.user == request.user or request.user.user_status == 'main' or 'manager' == request.user.user_status \
                or 'moderator' == request.user.user_status:
            return True
        return False


class ManagerIsAuthorPermission(BasePermission):
    def has_object_permission(self, request, view, obj):
        if obj.manager == request.user or request.user.user_status == 'main' or 'manager' == request.user.user_status \
                or 'moderator' == request.user.user_status:
            return True
        return False


class Self(IsAdminUser):
    def has_object_permission(self, request, view, obj):
        if request.user and request.user.is_staff:
            return True
        elif request.user and isinstance(obj, get_user_model()) and obj == request.user:
            return True
        return False


class IsMainPermission(BasePermission):
    def has_permission(self, request, view):
        if 'main' == request.user.user_status or 'manager' == request.user.user_status \
                or 'moderator' == request.user.user_status:
            return True
        return False


class IsEntityAuthenticated(BasePermission):
    def has_permission(self, request, view):
        if request.user.is_authenticated and request.user.user_status == 'entity':
            return True
        return False

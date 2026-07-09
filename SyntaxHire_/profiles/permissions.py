from rest_framework import permissions

class IsOwnerOfProfile(permissions.BasePermission):
    """
    Custom permission to only allow owners of a profile to view or edit it.
    """
    def has_object_permission(self, request, view, obj):
        # The profile object has a direct 'user' OneToOne relationship
        return obj.user == request.user
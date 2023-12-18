from rest_framework import permissions


class IsManager(permissions.BasePermission):
    def has_permission(self, request, view):
        """Implement your logic to check if the user is a manager"""
        if request.user.groups.filter(name="Manager").exists():
            return True
        return False


class IsDeliveryCrew(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.user.groups.filter(name="Delivery Crew").exists():
            return True
        return False

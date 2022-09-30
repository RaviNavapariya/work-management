from rest_framework import permissions
from django.contrib.auth.models import User
from .models import Workorder
from rest_framework.response import Response
class WorkOrderPermission(permissions.BasePermission):    
    def has_permission(self, request, view):
        user = User.objects.get(username=request.user)
        group = str(user.groups.all().first())
        if group == 'System Admin' or request.method == 'GET':
            return True
        if group == 'Manager' and request.method == 'PUT':
            return True
        if group == 'Normal User' and request.method == 'PUT':
            return True            
        return False
       

class WorkAssignPermission(permissions.BasePermission):
    def has_permission(self, request, view):
        user = User.objects.get(username=request.user)
        group = str(user.groups.all().first())
        if group == 'Manager'and request.method == 'PUT':            
                return True
        return False

class CommentPostPermission(permissions.BasePermission):
    def has_permission(self, request, view):
        user = User.objects.get(username=request.user)
        group = str(user.groups.all().first())
        task = request.data.get('task')
        getTask = Workorder.objects.get(id= task)
        assign_from_id = getTask.assign_from.id
        assign_to_id = getTask.assign_to.id
        if group == 'Manager' or group == 'Normal User' and request.method =='POST':
            if group == 'Manager':
                if assign_from_id == user.id:
                    return True
                else:
                    return False
            elif group == 'Normal User':
                if assign_to_id == user.id:
                    return True
                return False
        return False
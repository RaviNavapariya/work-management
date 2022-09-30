from django.contrib import admin
from .models import *



@admin.register(Workorder)
class WorkorderAdmin(admin.ModelAdmin):
    list_display = ('id','task_name','get_task_given_by','description','priority','status')

    def get_task_given_by(self, obj):
        return obj.task_given_by.username

    # 'get_assign_from','get_assign_to',
    # def get_assign_to(self, obj):
    #     return obj.assign_to.username

    # def get_assign_from(self, obj):
    #     return obj.assign_from.username


# admin.site.register(Workorder,WorkorderAdmin)
@admin.register(UserComment)
class WorkorderAdmin(admin.ModelAdmin):
    list_display = ('id','task','body','created','comment_by')

    def get_comment_by(self, obj):
        return obj.comment_by.username

    def get_task(self,obj):
        return obj.task.task_name

        
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

PRIORITY_CHOICES = (
    ("low", "LOW"),
    ("medium", "MEDIUM"),
    ("high", "HIGH"),
)

STATUS_CHOICES = (
    ("completed", "COMPLETED"),
    ("incompleted", "INCOMPLETED"),
    ("blocked", "BLOCKED"),
)

class Workorder(models.Model):
    task_name = models.CharField(max_length=20)
    task_given_by = models.ForeignKey(User, related_name='task_given_by', on_delete=models.CASCADE)
    description = models.TextField()
    assign_to = models.ForeignKey(User, related_name='assign_to', on_delete=models.CASCADE,  null=True)
    assign_from = models.ForeignKey(User, related_name='assign_from', on_delete=models.CASCADE,  null=True)
    priority = models.CharField(max_length=50, choices=PRIORITY_CHOICES)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES)
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.task_name

class UserComment(models.Model):
    comment_by = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='comment_user', null=True)
    task = models.ForeignKey(
        Workorder, related_name='comment_user', on_delete=models.CASCADE)
    body = models.TextField(blank=False)
    created = models.DateTimeField(auto_now_add=True)
    images = models.FileField(upload_to='media/')
    # parent_comment = models.ForeignKey('self' , null=True , blank=True , on_delete=models.CASCADE , related_name='replies')

    class Meta:
        ordering = ['-created']

    def __str__(self):
        return self.comment_by.username
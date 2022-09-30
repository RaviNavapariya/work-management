from django.contrib import admin
from django.urls import path
from . import views

urlpatterns = [
    path('register/', views.RegisterAPIView.as_view() , name='register'),
    path('login/',views.LoginAPIView.as_view(), name='login'),
    path('workmanagement/',views.WorkorderManagementAPIView.as_view(), name='workmanagement'),
    path('workmanagement/<int:pk>/',views.WorkorderManagementAPIView.as_view(), name='workmanagement'),
    path('workassign/<int:pk>/',views.WorkAssignView.as_view(), name='workassign'),
    # path('comments/', views.CommentList.as_view()),
    # path('comments/<int:pk>/', views.CommentDetail.as_view()),
    path('comment-create/',views.CommentCreateAPIView.as_view()),
]

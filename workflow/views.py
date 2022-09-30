from rest_framework.views import APIView
from .serializers import *
from rest_framework.response import Response
from rest_framework import status
from .models import Workorder
from django.http import Http404
from django.contrib.auth.models import Group, User
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import AuthenticationFailed
from rest_framework_simplejwt.tokens import RefreshToken
from workflow.permissions import WorkOrderPermission, WorkAssignPermission, CommentPostPermission
from django.conf import settings
from django.core.mail import send_mail

def get_tokens_for_user(user):
    refresh = RefreshToken.for_user(user)

    return {
        'refresh': str(refresh),
        'access': str(refresh.access_token),
    }

class RegisterAPIView(APIView):
    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class LoginAPIView(APIView):
    # authentication_classes = [JWTAuthentication]
    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')
        user = User.objects.filter(username=username).first()
        if user is None:
            raise AuthenticationFailed("User Name Does Not Exist")

        if not user.check_password(password):
            raise AuthenticationFailed("Password Invalid!")
        data = {
            'id':user.id,
            'username':user.username,
            'password':user.password,
            'token': get_tokens_for_user(user)
        }
        return Response(data)

class WorkorderManagementAPIView(APIView):
    permission_classes = [WorkOrderPermission]

    def get_object(self, pk):
        try:
            return Workorder.objects.get(pk=pk)
        except Workorder.DoesNotExist:
            raise Http404

    def get(self, request, pk=None):
        assign_to_user = request.user.id
        user = User.objects.get(username=request.user)
        group = str(user.groups.all().first())
        try:
            if pk is not None:
                if group == 'Normal User':
                    login_user = Workorder.objects.filter(assign_to_id=assign_to_user)
                    list_login_user = list(login_user.values())
                    for dict in list_login_user:
                        print(dict['assign_to_id'])                        
                        try:
                            login_user = Workorder.objects.get(assign_to_id=assign_to_user,pk=pk)
                            serializer = WorkorderCreateSerializer(login_user)
                            return Response(serializer.data)
                        except Workorder.DoesNotExist:
                            return Response({"Message":"This Task is not assign to you. So, You can not access this task".format(pk)})
                else:
                    workorder = Workorder.objects.get(id=pk)
                    serializer = WorkorderCreateSerializer(workorder)
                    return Response(serializer.data)
            else:                
                if group == 'Normal User':
                    login_user = Workorder.objects.filter(assign_to_id=assign_to_user)
                    list_login_user = list(login_user.values())
                    for dict in list_login_user:
                        print(dict['assign_to_id'])
                        login_user = Workorder.objects.filter(assign_to_id=assign_to_user)
                        serializer = WorkorderCreateSerializer(login_user, many=True)
                        return Response(serializer.data)
                # if group == 'Manager':
                #     login_manager = Workorder.objects.filter(assign_from_id=assign_to_user)
                #     list_login_user = list(login_manager.values())
                #     for dict in list_login_user:
                #         if dict['assign_from_id'] == assign_to_user:
                #             login_manager = Workorder.objects.filter(assign_from_id=assign_to_user)
                #             serializer = WorkorderCreateSerializer(login_manager, many=True)
                #             return Response(serializer.data)
                else:
                    workorder = Workorder.objects.all()
                    serializer = WorkorderCreateSerializer(workorder, many=True)
                    return Response(serializer.data)
        except Workorder.DoesNotExist:
            print("__________DoesNotExist____________")
            return Response({"message":"{} is not valid Endpoint id, Please Enter valid Endpoint id".format(pk)})

    def post(self,request):      
        serializer = WorkorderCreateSerializer(data=request.data)        
        if serializer.is_valid(raise_exception=True):         
            serializer.save(task_given_by=request.user)
            return Response(serializer.data,status=status.HTTP_201_CREATED)    
        

    def put(self, request, pk):
        workflow = Workorder.objects.get(pk=pk)
        user = User.objects.get(username=request.user)
        group = str(user.groups.all().first())
        if group == 'Normal User':
            serializer = WorkorderEditByNormalUserSerializer(workflow, data=request.data, partial=True)
        elif group == 'Manager':
            serializer = WorkorderEditByManagerSerializer(workflow, data=request.data, partial=True)
        else:
            serializer = WorkorderCreateSerializer(workflow, data=request.data, partial=True)
        print("<<<<<<<<<<<<<___________serializer______________>>>>>>>>>>>>>>>",serializer)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        workflow = self.get_object(pk)
        workflow.delete()
        return Response({"message": "Article with {} has been deleted.".format(workflow)}, status=status.HTTP_204_NO_CONTENT)


class WorkAssignView(APIView):    
    permission_classes = [WorkAssignPermission]
    def put(self, request, pk):
        login_user_email = request.user.email
        normal_user = request.data.get('assign_to')
        print("<<<<<<<<<<<<<<<<_____NORMAL USER______>>>>>>>>>>>>>>>>>>>>",normal_user)
        normal_user_email = User.objects.filter(id=normal_user).values('email')
        if len(normal_user_email) > 0:
             normal_user_email = normal_user_email[0]['email']
        normal_user_name = User.objects.filter(id=normal_user).values('username')
        if len(normal_user_name) > 0:
            normal_user_name = normal_user_name[0]['username']
        user = User.objects.get(username=request.user)
        print("<<<<<<<<<<___________user_____________>>>>>>>>>>>>",user)
        group = str(user.groups.all().first())        
        if pk is not None:
            try:
                workflow = Workorder.objects.get(pk=pk)
            except Workorder.DoesNotExist:
                return Response({"message":"User with id {} Does Not Exist in Workorder Model!!!!".format(pk)})
            serializer = WorkorderAssignSerializer(workflow, data=request.data)
            if serializer.is_valid():
                normal_user = request.data.get('assign_to')
                assign_to_useruser_groupp = User.objects.filter(id=normal_user).groups.all().first()
                print("________________assign_to_user_groupAAAAAAAAAAa________________________",assign_to_useruser_groupp)
                if str(assign_to_useruser_groupp)=='Normal User':
                    # if str(i)== assign_to_user_group:
                    subject = 'welcome to WorkManagement World'
                    message = f'Hi {normal_user_name}, thank you, this task is assign to you by{user}'
                    email_from = login_user_email
                    print("<<<<<<,<<<<<<<<<_____________login_user_email____________________>>>>>>>>>>>>>>>>>>>",email_from)
                    recipient_list = [normal_user_email]
                    print("<<<<<<<<<<<<______________normal_user_email_______________>>>>>>>>>>>>>>>>",recipient_list)
                    send_mail( subject, message, email_from, recipient_list )
                    print("<<<<<<<<__________send_mail_____________>>>>>>>>>>>",send_mail)
                    serializer.save(assign_from=request.user,assign_to=user)
                    return Response(serializer.data, status=status.HTTP_200_OK)
                return Response({'message':'You have assign this {} only for Normal User Group Member User.'.format(workflow)})
        return Response(serializer.errors)

                # assign_to_user_group = str(user.groups.all().first())
                # all_group = list(Group.objects.all())
                # for i in all_group:

class CommentCreateAPIView(APIView):
    permission_classes = [CommentPostPermission]
    def post(self,request):
        user = User.objects.get(username=request.user)
        group = str(user.groups.all().first())
        serializer = CommentSerializer(data=request.data) 
        if serializer.is_valid():           
            serializer.save(comment_by=request.user)
            return Response(serializer.data,status=status.HTTP_201_CREATED)
        return Response(serializer.errors)
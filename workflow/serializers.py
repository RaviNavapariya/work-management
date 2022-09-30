from rest_framework import serializers
from django.contrib.auth.models import Group, User
from .models import *

class GroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = Group
        fields = ('name',)
    
class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(style = {'input':'password'},max_length=20)
    email = serializers.EmailField(required=True)

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'password','groups']

    def create(self, validated_data):
        group_name = self.validated_data.pop("groups")
        if len(group_name)==1:
            user = User(
                email=validated_data['email'],
                username=validated_data['username'],
                first_name=validated_data['first_name'],
                last_name=validated_data['last_name'],           
            )
            user.set_password(validated_data['password'])
            user.save()
            group_name[0].user_set.add(user)
            # user.groups.add(Group.objects.get(name='System Admin'))
            return user
        else:
            raise serializers.ValidationError({"detail": "You have input more than one Group"})

class CommentSerializer(serializers.ModelSerializer):
    comment_by = serializers.ReadOnlyField(source='comment_by.username')
    images = serializers.FileField(max_length=100000,allow_empty_file=False,
        use_url=True )
    class Meta:
        model = UserComment
        fields = ['id', 'body','task','comment_by','created','images']

    # def create(self, validated_data):
    #     # task=Comment.objects.latest('created')
    #     # print("___________task__________________",task)
    #     images=validated_data.pop('images')
    #     print("_________________________images_________________________",type(images))
    #     for img in images:
    #         print("______________IMAGEIMAGE____________________________",type(img))
    #         photo=Comment.objects.create(images=img,**validated_data)
    #         print("___________________photo_______________________",photo)
    #     return photo

class WorkorderCreateSerializer(serializers.ModelSerializer):
    task_given_by = serializers.ReadOnlyField(source='task_given_by.username')
    comments = serializers.SerializerMethodField()
    class Meta:
        model = Workorder
        fields = ['id','task_name','task_given_by','description','priority','status','comments']

    def get_comments(self, obj):
        comments_query = UserComment.objects.filter(
            task_id=obj.id)
        serializer = CommentSerializer(comments_query, many=True)
        return serializer.data
    

class WorkorderEditByNormalUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = Workorder
        fields = ['id','status']

class WorkorderEditByManagerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Workorder
        fields = ['id','description','priority','status']

class WorkorderAssignSerializer(serializers.ModelSerializer):
    assign_to = serializers.ReadOnlyField(source='assign_to.username')
   
    class Meta:
        model = Workorder
        fields = ['id','assign_to']

class LoginSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['username','password']
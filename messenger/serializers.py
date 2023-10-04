from rest_framework import serializers
from .models import *
from rest_framework.serializers import ModelSerializer
import django_filters

# class UserSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = User
#         fields = ('id', 'email', 'fullname', 'is_active', 'is_staff', 'date_joined', 'password', 'user_type')
    
# class LoginSerializer(serializers.ModelSerializer):

#     class Meta:
#         model = User
#         fields = ('email', 'password')
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('slug','id', 'email', 'fullname', 'telephone', 'is_active', 'is_staff','admin' ,'password_reset_count', 'user_type', 'adresse', 'password', 'last_login','is_archive')

class UserGetSerializer(serializers.ModelSerializer):
   
    class Meta:
        model = User
        exclude = (
            'user_permissions', 'groups', 'is_superuser','password','is_active','last_login','password_reset_count')

class UserStatutSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id','is_active')

class AdminUserSerializer(ModelSerializer):

    class Meta:
        model = AdminUser
        exclude = (
            'user_permissions', 'groups', 'is_superuser',
            'is_staff')

    def create(self, validated_data, **extra_fields):
        user = self.Meta.model(**validated_data)
        user.set_password(validated_data['password'])
        user.user_type = ADMIN
        user.admin_type = ADMIN
        user.is_active = True
        user.save()
        return user
class UserRegisterSerializer(ModelSerializer):

    class Meta:
        model = User
        exclude = (
            'user_permissions', 'groups', 'is_superuser', 'is_staff')

    def create(self, validated_data, **extra_fields):
        user = self.Meta.model(**validated_data)
        user.set_password(validated_data['password'])
        user.is_active = True
        user.save()
        return user

class AdminUserGetSerializer(serializers.ModelSerializer):
    class Meta:
        model = AdminUser
        exclude = (
            'user_permissions', 'groups', 'is_superuser',
            'is_staff', 'password')

class PasswordResetSerializer(serializers.Serializer):
    model = User
    """
    Serializer for password change endpoint.
    """
    code = serializers.CharField(required=True)
    email = serializers.CharField(required=True)
    new_password_confirm = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True)


class RequestPasswordSerializer(serializers.Serializer):
    model = User
    """
    Serializer for password change endpoint.
    """
    email = serializers.CharField(required=True)


class ChangePasswordSerializer(serializers.Serializer):
    model = User
    """
    Serializer for password change endpoint.
    """
    old_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True)


class LoginSerializer(ModelSerializer):

    class Meta:
        model = User
        fields = ('email', 'password')


class SuppressionCompteSerializer(ModelSerializer):

    class Meta:
        model = User
        fields = ('password',)


class AccountActivationSerializer(ModelSerializer):

    class Meta:
        model = AccountActivation
        fields = '__all__'


class MessageSerializer(ModelSerializer):

    class Meta:
        model = Message
        fields = '__all__'

class SendMessageSerializer(ModelSerializer):

    class Meta:
        model = Message
        fields = ('sender', 'receiver', 'content')

class ReceiveMessageSerializer(ModelSerializer):

    class Meta:
        model = Message
        fields = ('sender', 'receiver', 'content')

from rest_framework import serializers
from .models import User
from django.utils.translation import gettext_lazy as _

from django.contrib.auth import authenticate




class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'email', 'user_type', 'library_accepted', 'is_verified', 'location', 'language', 'new_email', 'full_name']
        
    
class UserSignupSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['email', 'password', 'user_type','first_name', 'last_name']
        extra_kwargs = {
            'password': {'write_only': True},
        }
        
    def create(self, validated_data):
        
        user = User.objects.create_user(**validated_data)
        return user
    

class ClientUserLoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField()
        
    def validate(self, data):
        email = data.get('email')
        password = data.get('password')
        user_type = User.objects.get(email=email).user_type
        if email and password and user_type == 'Client':
            
            user = authenticate(email=email, password=password)
            if user:
                if user.is_verified:
                    data['user'] = user
                else:
                    msg = _('Email is not verified.')
                    raise serializers.ValidationError(msg)
            else:
                msg = _('Unable to login with given credentials.')
                raise serializers.ValidationError(msg)
        else:
            msg = _('Must include "email" and "password".')
            raise serializers.ValidationError(msg)
        
        return data
    
class LibrarianUserLoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField()
        
    def validate(self, data):
        email = data.get('email')
        password = data.get('password')
        user_type = User.objects.get(email=email).user_type
        if email and password and user_type == 'Librarian':
            
            user = authenticate(email=email, password=password)
            if user:
                if user.is_verified and user.library_accepted:
                    data['user'] = user
                else:
                    msg = _('Email is not verified.')
                    raise serializers.ValidationError(msg)
            else:
                msg = _('Unable to login with given credentials.')
                raise serializers.ValidationError(msg)
        else:
            msg = _('Must include "email" and "password".')
            raise serializers.ValidationError(msg)
        
        return data
    
    
class UserChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField()
    new_password = serializers.CharField()
    
    def validate(self, data):
        old_password = data.get('old_password')
        new_password = data.get('new_password')
        user = self.context['request'].user
        if not user.check_password(old_password):
            raise serializers.ValidationError({'old_password': _('Old password is incorrect.')})
        else:
            user.set_password(new_password)
            user.save
        
        return data
    
    def update(self, instance, validated_data):
        instance.set_password(validated_data['new_password'])
        instance.save()
        return instance
    

class VerifyEmailSerializer(serializers.Serializer):
    otp = serializers.CharField()
    email = serializers.EmailField()
    
    def validate(self, data):
        otp = data.get('otp')
        email = data.get('email')
        print(email,'#'*20)
        user = User.objects.get(email=email)
        if otp == user.otp:
            user.is_verified = True
            user.save()
        else:
            raise serializers.ValidationError({'otp': _('Invalid OTP.')})
        
        return data
    
    
class UpdateUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'location', 'language', ]
        
    def update(self, instance, validated_data):
        instance.first_name = validated_data.get('first_name', instance.first_name)
        instance.last_name = validated_data.get('last_name', instance.last_name)
        instance.location = validated_data.get('location', instance.location)
        instance.language = validated_data.get('language', instance.language)
        instance.save()
        return instance
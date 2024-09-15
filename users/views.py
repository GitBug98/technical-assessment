from .serializers import UserSerializer, ClientUserLoginSerializer, LibrarianUserLoginSerializer, UserSignupSerializer, UserChangePasswordSerializer, VerifyEmailSerializer,UpdateUserSerializer
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from django.utils.translation import gettext_lazy as _
from django.contrib.auth import authenticate
from .models import User
from rest_framework.authtoken.models import Token
import pyotp




class UserSignupView(generics.CreateAPIView):
    serializer_class = UserSignupSerializer
    permission_classes = (permissions.AllowAny,)

    def post(self, request, *args, **kwargs):
        serializer = UserSignupSerializer(data=request.data)
        
        if serializer.is_valid(raise_exception=True):
            totp = pyotp.TOTP('base32secret3232')
            now_otp = totp.now()
            serializer.validated_data['otp'] = now_otp
            # sent otp to user email
            
            
            user = serializer.save()
            serializer = UserSerializer(user)
            data = serializer.data
            return Response(data, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    
class VerifyEmailView(APIView):
    permission_classes = (permissions.AllowAny,)
    
    def post(self, request):
        serializer = VerifyEmailSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            user = User.objects.get(email=serializer.validated_data['email'])
            user.is_verified = True
            token, created = Token.objects.get_or_create(user=user)
            user.save()
            data = {'token': token.key,
                    'email': user.email, 
                    'user_type': user.user_type,
                    'is_verified': user.is_verified,
                    'message': _('Email verified successfully.')
                    }
            return Response(data, status=status.HTTP_200_OK)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    

class UserLoginView(APIView):
    permission_classes = (permissions.AllowAny,)
    
    def post(self, request):
        user_type = User.objects.get(email=request.data.get('email')).user_type
        
        if user_type == 'Client':
            serializer = ClientUserLoginSerializer(data=request.data)
        else:
            serializer = LibrarianUserLoginSerializer(data=request.data)
        
        if serializer.is_valid(raise_exception=True):
            user = serializer.validated_data['user']
            Token.objects.filter(user=user).delete()
            new_token, _created = Token.objects.get_or_create(user=user)
            data = {'token': new_token.key,
                    'email': user.email, 
                    'user_type': user.user_type,
                    'is_verified': user.is_verified,
                    'message': _('Login successful.')
                    }
            return Response(data, status=status.HTTP_200_OK)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    
class UserChangePasswordView(APIView):
    permission_classes = (permissions.IsAuthenticated,)
    
    def post(self, request):
        # set context to request in order to get user object
        user = request.user
        request.data['user'] = user
        serializer = UserChangePasswordSerializer(data=request.data, context={'request': request})
        if serializer.is_valid(raise_exception=True):
            user = request.user
            user.set_password(serializer.validated_data['new_password'])
            user.save()
            return Response({'message': _('Password changed successfully.')}, status=status.HTTP_200_OK)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    


class UserDetailView(generics.RetrieveAPIView):
    serializer_class = UserSerializer
    permission_classes = (permissions.IsAuthenticated,)
    
    def get_object(self):
        return self.request.user




class UpdateUserView(generics.UpdateAPIView):
    serializer_class = UpdateUserSerializer
    permission_classes = (permissions.IsAuthenticated,)
    
    def get_object(self):
        return self.request.user
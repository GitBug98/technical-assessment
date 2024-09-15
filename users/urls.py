from .views import UserSignupView, UserLoginView, UserChangePasswordView, VerifyEmailView, UserDetailView, UpdateUserView
from django.urls import path



urlpatterns = [
    path('signup/', UserSignupView.as_view(), name='signup'),
    path('login/', UserLoginView.as_view(), name='login'),
    path('change-password/', UserChangePasswordView.as_view(), name='change-password'),
    path('verify-email/', VerifyEmailView.as_view(), name='verify-email'),
    path('user-detail/', UserDetailView.as_view(), name='user-detail'),
    path('update-user/', UpdateUserView.as_view(), name='update-user'),
    
    
]
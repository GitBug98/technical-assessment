
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.conf import settings
from django.contrib.auth.models import AbstractUser, Permission
from django.contrib.auth.models import UserManager as BaseUserManager
from location_field.models.plain import PlainLocationField

class UserManager(BaseUserManager):
    use_in_migrations = True

    def _create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError(_('The given email number must be set'))

        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_superuser', False)
        extra_fields.setdefault('is_staff', False)
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self._create_user(email, password, **extra_fields)


class User(AbstractUser):
    # Define roles based on the project requirement (Admin, Client, Librarian, etc.)
    USER_TYPES = (
        ('Admin', _('Admin')),
        ('Client', _('Client')),
        ('Librarian', _('Librarian')),
    )
    
    user_type = models.CharField(_('user type'), max_length=10, choices=USER_TYPES, default='Client')
    library_accepted = models.BooleanField(_('library accepted'), default=False)
    email = models.EmailField(_('email address'), unique=True)
    username = None  # Disabling username as we are using email for login
    otp = models.CharField(_('otp'), max_length=6, blank=True, null=True)  # OTP for verification
    is_verified = models.BooleanField(_('is verified'), default=False)
    location = PlainLocationField(based_fields=['city'], zoom=7, null=True)  # You can adjust 'based_fields' as needed
    language = models.CharField(_('preferred language'), max_length=10, default='en', choices=settings.LANGUAGES)
    new_email = models.CharField(_('new email'), max_length=20, blank=True, null=True)



    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS: list = ['password']  # As per your requirement, only password is needed

    # Custom Manager
    objects = UserManager()

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"

    class Meta:
        ordering = ['-id']
        verbose_name = _('User')
        verbose_name_plural = _('Users')

    def __str__(self):
        return str(self.email)
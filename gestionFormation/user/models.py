from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.core.validators import RegexValidator
from django.db import models

class CustomUserManager(BaseUserManager):

    def default_profile_image():
        return 'default_profile_picture.jpg'

    def create_user(self, email, password=None, cin=None, organisme=None, role=None,img=None, **extra_fields):
        if not email:
            raise ValueError("The Email field must be set")
        email = self.normalize_email(email)
        user = self.model(email=email, cin=cin, organisme=organisme, role=role,img=img, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, cin=None, organisme=None, role='Admin',img=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(email, password, cin, organisme, role,img, **extra_fields)

class Profile(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(unique=True)
    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=30)
    cin_regex = RegexValidator(regex=r'^\d{8}$', message="CIN must be an 8-digit number.")
    cin = models.CharField(validators=[cin_regex], max_length=8)  # 8-digit number
    organisme = models.CharField(max_length=255)  # String field for organisme
    role = models.CharField(max_length=255)  # String field for role
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    img = models.ImageField(default='def.png',null=True,blank=True) # Image field for profile image

    objects = CustomUserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name', 'cin', 'organisme', 'role']

    def __str__(self):
        return self.email
    
    def set_Role(self, new_role):
        self.role = new_role


import uuid
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models
from core.models import TimeStampedModel

class CustomUserManager(BaseUserManager):
    """Custom manager for CustomUser where email is the unique identifier for authentication."""
    
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('The Email field must be set')
        
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('user_type', 'ADMIN')

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self.create_user(email, password, **extra_fields)


class CustomUser(AbstractUser, TimeStampedModel):
    """
    SyntaxHire Custom User Model.
    Authentication requires only email and password.
    Role registration is deferred to the profile completion stage.
    """
    class UserType(models.TextChoices):
        PENDING = 'PENDING', 'Pending Assignment' # Yeni kayıt olan, henüz rol seçmemiş kullanıcı
        DEVELOPER = 'DEVELOPER', 'Developer'
        COMPANY = 'COMPANY', 'Company/Client'
        ADMIN = 'ADMIN', 'Admin'

    # Standart otomatik artan ID yerine UUID atıyoruz
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    # Remove the default username field
    username = None
    email = models.EmailField(unique=True, verbose_name="Email Address")


    
    # Defaults to PENDING so they can choose their role later during onboarding
    user_type = models.CharField(
        max_length=20, 
        choices=UserType.choices, 
        default=UserType.PENDING,
        verbose_name="User Type"
    )

    is_verified = models.BooleanField(default=False, verbose_name="Is Verified")
    
    # Authentication configurations
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []  # Only email and password required

    objects = CustomUserManager()

    def __str__(self):
        return f"{self.email} ({self.get_user_type_display()})"
    
    
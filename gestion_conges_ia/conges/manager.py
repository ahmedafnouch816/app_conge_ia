
# managers.py
from django.contrib.auth.models import BaseUserManager

class UserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        """
        Create and return a regular user with an email and password.
        """
        if not email:
            raise ValueError('The Email field must be set')
        
        # Normalize the email to lowercase
        email = self.normalize_email(email)
        
        # Create the user instance with the email and any extra fields
        user = self.model(email=email, **extra_fields)
        
        # Set the password for the user
        user.set_password(password)
        
        # Save the user to the database
        user.save(using=self._db)
        
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        """
        Create and return a superuser with email, password, and required fields.
        """
        # Ensure that the superuser has necessary flags
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        # Use create_user method to create the superuser
        return self.create_user(email, password, **extra_fields)

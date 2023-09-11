from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType
from django.db import models

# Define a custom permission (replace 'app_name' with your app's name)
class CanDeleteMessagePermission(models.Model):
    class Meta:
        managed = False  # This model won't create database tables
        default_permissions = ()  # Disable default permissions

    # Define a unique codename for the permission
    codename = 'delete_message'
    name = 'Can delete a message'

    def save(self, *args, **kwargs):
        content_type = ContentType.objects.get_for_model(self.__class__)
        permission, created = Permission.objects.get_or_create(
            codename=self.codename,
            content_type=content_type,
        )
        return permission

# Create an instance of the custom permission
CanDeleteMessagePermission().save()

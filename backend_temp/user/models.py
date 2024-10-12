from django.contrib.auth.models import AbstractUser

from django.db import models


class CustomUser(AbstractUser):
    username = models.CharField(max_length=24, unique=True)
    email = models.EmailField(unique=True)

    def __str__(self):
        return self.username

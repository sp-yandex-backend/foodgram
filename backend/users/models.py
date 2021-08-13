from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    email = models.EmailField(max_length=254, unique=True)
    username = models.CharField(max_length=120, unique=True)
    first_name = models.CharField(max_length=120)
    last_name = models.CharField(max_length=120)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username", "first_name", "last_name"]

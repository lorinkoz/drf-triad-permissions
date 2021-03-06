from django.contrib.auth.models import AbstractBaseUser
from django.db import models


class User(AbstractBaseUser):

    username = models.SlugField(unique=True)

    USERNAME_FIELD = "username"

    def get_permissions(self):
        return [
            "user::all::read",  # Read all users
            f"user::id:{self.id}::all",  # Do anything with self, by ID
            "entity::all::read",  # Read all entities
            f"entity::user:{self.username}::all",  # Do anything with entities that belog to self, by username
        ]


class Entity(models.Model):

    slug = models.SlugField()

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="+")

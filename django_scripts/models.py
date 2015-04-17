from django.db import models


class Script(models.Model):
    name = models.CharField(max_length=200, unique=True)
    applied = models.DateField(auto_now_add=True)

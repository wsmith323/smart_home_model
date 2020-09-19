from django.db import models


class Manufacturer(models.Model):
    id = models.UUIDField(primary_key=True)
    name = models.CharField(max_length=255)
    # Additional manufacturer fields like address, etc.

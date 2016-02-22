from django.db import models


class TestModel(models.Model):
    __test__ = False

    name = models.TextField()

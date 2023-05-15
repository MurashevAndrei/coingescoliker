from django.db import models

class Coin(models.Model):
    coin_name = models.CharField(max_length=200)
    pub_date = models.DateTimeField('date published')
    total_value = models.IntegerField()
    difference = models.IntegerField()

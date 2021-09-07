from django.contrib.auth.models import User
from django.db import models

# Create your models here.
class BankAccount(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    balance = models.DecimalField(max_digits=10, decimal_places=2)
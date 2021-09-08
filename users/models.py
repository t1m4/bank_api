from django.contrib.auth.models import User
from django.db import models


# Create your models here.
class BankAccount(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    number = models.BigIntegerField(unique=True, db_index=True)
    balance = models.DecimalField(max_digits=10, decimal_places=2)


class Operation(models.Model):
    amount = models.PositiveIntegerField()
    message = models.CharField(max_length=100)
    date = models.DateTimeField(auto_now_add=True)
    sender = models.ForeignKey(BankAccount, on_delete=models.CASCADE, related_name='sender')
    receiver = models.ForeignKey(BankAccount, on_delete=models.CASCADE, related_name='receiver')

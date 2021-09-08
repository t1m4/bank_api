from decimal import Decimal

from django.contrib.auth.models import User
from django.core.validators import MinValueValidator
from django.db import models
from django.utils import timezone


# Create your models here.
class BankAccount(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    balance = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(Decimal('0.01'))])


class Operation(models.Model):
    amount = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(Decimal('0.01'))])
    message = models.CharField(max_length=100, blank=True)
    date = models.DateTimeField(auto_now_add=True)
    sender = models.ForeignKey(BankAccount, on_delete=models.CASCADE, related_name='sender')
    receiver = models.ForeignKey(BankAccount, on_delete=models.CASCADE, related_name='receiver')

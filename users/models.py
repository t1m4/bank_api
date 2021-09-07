from django.contrib.auth.models import User
from django.db import models
from django.utils import timezone


# Create your models here.
class BankAccount(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    balance = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f'{self.user}'


class Operation(models.Model):
    amount = models.PositiveIntegerField()
    message = models.CharField(max_length=100)
    date = models.DateTimeField(default=timezone.now)
    sender = models.ForeignKey(BankAccount, on_delete=models.CASCADE, related_name='sender')
    receiver = models.ForeignKey(BankAccount, on_delete=models.CASCADE, related_name='receiver')

    class Meta:
        unique_together = ['sender', 'receiver']

from decimal import Decimal

from django.db import transaction

from users.models import BankAccount


def transfer(sender: BankAccount, receiver: BankAccount, amount: Decimal):
    """
    Transfer money from one account to another
    """
    with transaction.atomic():
        sender.balance -= amount
        receiver.balance += amount
        sender.save(update_fields=['balance'])
        receiver.save(update_fields=['balance'])

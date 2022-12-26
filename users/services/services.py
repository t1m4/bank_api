from decimal import Decimal

from django.db import transaction

from users.models import BankAccount, Operation
from users.services.exceptions import SmallBalanceException, SenderReceiverEqualException


def transfer_service(sender: BankAccount, receiver: BankAccount, amount: Decimal, message: str):
    """
    Transfer money from one account to another
    """
    if amount > sender.balance:
        raise SmallBalanceException("Sender don't have enough money.", amount, sender.balance)
    if sender == receiver:
        raise SenderReceiverEqualException("Sender and receiver must not be equal.", sender, receiver)

    with transaction.atomic():
        sender.balance -= amount
        receiver.balance += amount
        sender.save(update_fields=['balance'])
        receiver.save(update_fields=['balance'])
        return Operation.objects.create(amount=amount, sender=sender, receiver=receiver, message=message)

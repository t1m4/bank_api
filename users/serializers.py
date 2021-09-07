from django.db import transaction
from rest_framework import serializers

from users.models import BankAccount, Operation


class BankAccountSerializer(serializers.ModelSerializer):
    class Meta:
        model = BankAccount
        fields = ['user', 'balance']


class OperationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Operation
        fields = ['amount', 'message', 'sender', 'receiver']


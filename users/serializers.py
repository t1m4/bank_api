from django.db import transaction
from rest_framework import serializers

from users.models import BankAccount, Operation


class BankAccountSerializer(serializers.ModelSerializer):
    class Meta:
        model = BankAccount
        fields = ['id', 'user', 'balance']


class OperationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Operation
        fields = ['amount', 'message', 'sender', 'receiver', 'date']


class TransferSerializer(serializers.ModelSerializer):
    class Meta:
        model = Operation
        fields = ['amount', 'message', 'sender', 'receiver']

    def validate(self, data):
        if data['amount'] > data['sender'].balance:
            raise serializers.ValidationError("Sender don't have enough money.")
        if data['sender'] == data['receiver']:
            raise serializers.ValidationError("Sender and receiver must not be equal.")
        return data

    def save(self, **kwargs):
        amount = self.validated_data['amount']
        with transaction.atomic():
            self.validated_data['sender'].balance -= amount
            self.validated_data['receiver'].balance += amount
            self.validated_data['sender'].save(update_fields=['balance'])
            self.validated_data['receiver'].save(update_fields=['balance'])
            return super(TransferSerializer, self).save(**kwargs)

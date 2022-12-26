from decimal import Decimal
from rest_framework import serializers

from users.models import BankAccount, Operation
from users.services.services import transfer_service


class BankAccountSerializer(serializers.ModelSerializer):
    class Meta:
        model = BankAccount
        fields = ['id', 'user', 'balance']


class OperationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Operation
        fields = ['amount', 'message', 'sender', 'receiver', 'date']


class TransferSerializer(serializers.Serializer):
    amount = serializers.IntegerField(min_value=0.01)
    sender = serializers.PrimaryKeyRelatedField(queryset=BankAccount.objects.all())
    receiver = serializers.PrimaryKeyRelatedField(queryset=BankAccount.objects.all())
    message = serializers.CharField(max_length=100, required=False, default='')


    def validate(self, data):
        if data['amount'] > data['sender'].balance:
            raise serializers.ValidationError("Sender don't have enough money.")
        if data['sender'] == data['receiver']:
            raise serializers.ValidationError("Sender and receiver must not be equal.")
        return data

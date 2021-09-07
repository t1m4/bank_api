# Create your views here.
from rest_framework import generics

from users.serializers import BankAccountSerializer, OperationSerializer


class CreateBankAccount(generics.CreateAPIView):
    serializer_class = BankAccountSerializer


class TransferView(generics.CreateAPIView):
    serializer_class = OperationSerializer

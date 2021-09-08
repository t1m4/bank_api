# Create your views here.
from django.db.models import Q
from rest_framework import generics, viewsets, mixins
from rest_framework.decorators import action
from rest_framework.response import Response

from users.models import BankAccount, Operation
from users.serializers import BankAccountSerializer, TransferSerializer, OperationSerializer


class CreateBankAccount(mixins.CreateModelMixin,
                        mixins.RetrieveModelMixin,
                        viewsets.GenericViewSet):
    serializer_class = BankAccountSerializer
    queryset = BankAccount.objects.all()

    def get_serializer_class(self):
        if self.action == 'get_transfer_history':
            return OperationSerializer
        return super(CreateBankAccount, self).get_serializer_class()

    @action(detail=True, methods=['get'], url_path='transfer_history', url_name='get_history')
    def get_transfer_history(self, request, pk=None):
        account = self.get_object()
        operations = Operation.objects.filter(Q(sender=account) | Q(receiver=account))
        serializer = self.get_serializer(operations, many=True)
        return Response(serializer.data)


class TransferView(generics.CreateAPIView):
    serializer_class = TransferSerializer

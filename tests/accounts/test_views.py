from decimal import Decimal

from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from tests.accounts.factories import BankAccountFactory, OperationFactory, UserFactory

from users.models import BankAccount, Operation



class TestBankAccountViewSet(APITestCase):

    def setUp(self):
        self.accounts_list_url = reverse('accounts-list')
        self.user = UserFactory.create()

    def test_can_create_account(self):
        account_data = {'user': self.user.id, 'balance': 100}
        response = self.client.post(self.accounts_list_url, account_data)
        result = response.json()

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIsNotNone(result.get('id'))
        self.assertIsNotNone(result.get('balance'))
        self.assertEqual(Decimal(result.get('balance')), Decimal(account_data['balance']))
        self.assertEqual(result.get('user'), account_data['user'])

    def test_cannot_create_account_with_negative_balance(self):
        account_data = {'user': self.user.id, 'balance': -100}
        response = self.client.post(self.accounts_list_url, account_data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


    def test_cannot_create_account_with_not_exist_user(self):
        account_data = {'user': self.user.id - 1, 'balance': 100}
        response = self.client.post(self.accounts_list_url, account_data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_can_get_account(self):
        account = BankAccountFactory.create()
        accounts_detail_url = reverse('accounts-detail', kwargs={'pk': account.id})
        response = self.client.get(accounts_detail_url)
        result = response.json()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(result.get('user'), account.user_id)
        self.assertEqual(Decimal(result.get('balance')), account.balance)

    def test_cannot_get_non_exist_account(self):
        account = BankAccountFactory.create()
        accounts_detail_url = reverse('accounts-detail', kwargs={'pk': account.id + 1})
        response = self.client.get(accounts_detail_url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_can_get_transfer_history(self):
        operation = OperationFactory.create(message='test')
        account_id = operation.sender_id
        accounts_get_history = reverse('accounts-get_history', kwargs={'pk': account_id})
        response = self.client.get(accounts_get_history)
        result = response.json()
        first_operation = result[0]

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsInstance(result, list)
        self.assertIsNotNone(first_operation.get('amount'))
        self.assertEquals(first_operation.get('message'), 'test')
        self.assertIsNotNone(first_operation.get('sender'))
        self.assertIsNotNone(first_operation.get('receiver'))
        self.assertIsNotNone(first_operation.get('date'))

        for operation in result:
            if operation['sender'] != account_id and operation['receiver'] != account_id:
                assert False, "We found operation not from this account"

    def test_cannot_get_transfer_history_from_non_exist_account(self):
        account = BankAccountFactory.create()
        accounts_get_history_url = reverse('accounts-get_history', kwargs={'pk': account.id + 1})
        response = self.client.get(accounts_get_history_url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


class TransferViewTest(APITestCase):
    def setUp(self):
        self.transfer_url = reverse('users-transfer')
        transer_operation = OperationFactory.create()
        self.sender = transer_operation.sender
        self.receiver = transer_operation.receiver

    def test_can_transfer(self):
        old_sender_balance = self.sender.balance
        old_receiver_balance = self.receiver.balance
        transfer_data = {
            "amount": 1,
            "message": "hello",
            "sender": self.sender.id,
            "receiver": self.receiver.id,
        }
        response = self.client.post(self.transfer_url, transfer_data)
        result = response.json()

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Decimal(result.get('amount')), Decimal(transfer_data['amount']))
        self.assertEqual(result.get('message'), transfer_data['message'])
        self.assertEqual(result.get('receiver'), transfer_data['receiver'])
        self.assertEqual(result.get('receiver'), transfer_data['receiver'])

        sender = BankAccount.objects.get(id=self.sender.id)
        receiver = BankAccount.objects.get(id=self.receiver.id)
        self.assertEqual(sender.balance, old_sender_balance - transfer_data['amount'])
        self.assertEqual(receiver.balance, old_receiver_balance + transfer_data['amount'])
        self.assertTrue(Operation.objects.filter(sender=sender, receiver=receiver).exists())

    def test_cannot_transfer_with_not_enough_balance(self):
        transfer_data = {
            "amount": self.sender.balance + 1,
            "message": "hello",
            "sender": self.sender.id,
            "receiver": self.receiver.id,
        }
        response = self.client.post(self.transfer_url, transfer_data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


    def test_cannot_transfer_with_equal_sender_and_receiver(self):
        transfer_data = {
            "amount": 1,
            "message": "",
            "sender": self.sender.id,
            "receiver": self.sender.id,
        }
        response = self.client.post(self.transfer_url, transfer_data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_can_transfer_without_message(self):
        transfer_data = {
            "amount": 1,
            "sender": self.sender.id,
            "receiver": self.receiver.id,
        }
        response = self.client.post(self.transfer_url, transfer_data)
        result = response.json()
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(result.get('message'), "")


from decimal import Decimal

from django.contrib.auth.models import User, Permission
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from users.models import BankAccount, Operation


def create_users(count_of_users):
    user_data = {
        'email': 'test1@mail.ru',
        'username': 'test',
        'password': 'alksdfjs',
    }
    for index in range(count_of_users):
        user_data = user_data.copy()
        user_data['email'] += str(index)
        user_data['username'] += str(index)
        user_data['password'] += str(index)
        User.objects.create(**user_data)

def create_accounts(count_of_accounts):
    users = User.objects.all()
    for user in users:
        account_data = {
            'user': user,
            'balance': 1
        }
        for index in range(count_of_accounts):
            account_data = account_data.copy()
            account_data['balance'] += index * 100
            BankAccount.objects.create(**account_data)

def create_transfer_history():
    accounts = list(BankAccount.objects.all())
    for index in range(len(accounts) - 1):
        operation_data = {
            'amount': 1,
            'message': 'hello',
            'sender': accounts[index],
            'receiver': accounts[index - 1],
        }
        Operation.objects.create(**operation_data)

class BankAccountViewSetTest(APITestCase):

    def setUp(self):
        self.accounts_list_url = reverse('accounts-list')
        self.accounts_detail_url = reverse('accounts-detail', kwargs={'pk': 1})
        self.accounts_get_history = reverse('accounts-get_history', kwargs={'pk': 1})

        create_users(count_of_users=2)
        create_accounts(count_of_accounts=2)
        create_transfer_history()

    def test_can_create_account(self):
        user = User.objects.first()
        account_data = {'user': user.id, 'balance': 100}
        response = self.client.post(self.accounts_list_url, account_data)
        result = response.json()

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIsNotNone(result.get('id'))
        self.assertIsNotNone(result.get('balance'))
        self.assertEqual(Decimal(result.get('balance')), Decimal(account_data['balance']))
        self.assertEqual(result.get('user'), account_data['user'])

    def test_cannot_create_account_with_negative_balance(self):
        user = User.objects.first()
        account_data = {'user': user.id, 'balance': -100}
        response = self.client.post(self.accounts_list_url, account_data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


    def test_cannot_create_account_with_not_exist_user(self):
        user = User.objects.first()
        account_data = {'user': user.id - 1, 'balance': 100}
        response = self.client.post(self.accounts_list_url, account_data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_can_get_account(self):
        account = BankAccount.objects.first()
        accounts_detail_url = reverse('accounts-detail', kwargs={'pk': account.id})
        response = self.client.get(accounts_detail_url)
        result = response.json()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(result.get('user'), account.user_id)
        self.assertEqual(Decimal(result.get('balance')), account.balance)

    def test_cannot_get_non_exist_account(self):
        account = BankAccount.objects.last()
        accounts_detail_url = reverse('accounts-detail', kwargs={'pk': account.id + 1})
        response = self.client.get(accounts_detail_url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


    def test_can_get_transfer_history(self):
        account = BankAccount.objects.first()
        accounts_get_history = reverse('accounts-get_history', kwargs={'pk': account.id})
        response = self.client.get(accounts_get_history)
        result = response.json()
        first_operation = result[0]

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsInstance(result, list)
        self.assertIsNotNone(first_operation.get('amount'))
        self.assertIsNotNone(first_operation.get('message'))
        self.assertIsNotNone(first_operation.get('sender'))
        self.assertIsNotNone(first_operation.get('receiver'))
        self.assertIsNotNone(first_operation.get('date'))

        for operation in result:
            if operation['sender'] != account.id and operation['receiver'] != account.id:
                assert False, "We found operation not from this account"

    def test_cannot_get_transfer_history_from_non_exist_account(self):
        account = BankAccount.objects.last()
        accounts_get_history_url = reverse('accounts-get_history', kwargs={'pk': account.id + 1})
        response = self.client.get(accounts_get_history_url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

class TransferViewTest(APITestCase):
    def setUp(self):
        self.transfer_url = reverse('users-transfer')

        create_users(count_of_users=2)
        create_accounts(count_of_accounts=2)

    def test_can_transfer(self):
        sender, receiver = BankAccount.objects.all()[:2]
        old_sender_balance = sender.balance
        old_receiver_balance = receiver.balance
        transfer_data = {
            "amount": 1,
            "message": "hello",
            "sender": sender.id,
            "receiver": receiver.id,
        }
        response = self.client.post(self.transfer_url, transfer_data)
        result = response.json()

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Decimal(result.get('amount')), Decimal(transfer_data['amount']))
        self.assertEqual(result.get('message'), transfer_data['message'])
        self.assertEqual(result.get('receiver'), transfer_data['receiver'])
        self.assertEqual(result.get('receiver'), transfer_data['receiver'])

        sender, receiver = BankAccount.objects.all()[:2]
        self.assertEqual(sender.balance, old_sender_balance - transfer_data['amount'])
        self.assertEqual(receiver.balance, old_receiver_balance + transfer_data['amount'])
        self.assertTrue(Operation.objects.filter(sender=sender, receiver=receiver).exists())

    def test_cannot_transfer_with_not_enough_balance(self):
        sender, receiver = BankAccount.objects.all()[:2]
        transfer_data = {
            "amount": sender.balance + 1,
            "message": "hello",
            "sender": sender.id,
            "receiver": receiver.id,
        }
        response = self.client.post(self.transfer_url, transfer_data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


    def test_cannot_transfer_with_equal_sender_and_receiver(self):
        sender = BankAccount.objects.first()
        transfer_data = {
            "amount": 1,
            "message": "",
            "sender": sender.id,
            "receiver": sender.id,
        }
        response = self.client.post(self.transfer_url, transfer_data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_can_transfer_without_message(self):
        sender, receiver = BankAccount.objects.all()[:2]
        transfer_data = {
            "amount": 1,
            "sender": sender.id,
            "receiver": receiver.id,
        }
        response = self.client.post(self.transfer_url, transfer_data)
        result = response.json()
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(result.get('message'), "")


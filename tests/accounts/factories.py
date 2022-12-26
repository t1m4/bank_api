from django.contrib.auth.models import User
from factory import SubFactory, fuzzy
from factory.django import DjangoModelFactory

from users import models


class UserFactory(DjangoModelFactory):
    username = fuzzy.FuzzyText()
    email = fuzzy.FuzzyText(suffix="@mail.ru")

    class Meta:
        model = User


class BankAccountFactory(DjangoModelFactory):
    user = SubFactory(UserFactory)
    balance = fuzzy.FuzzyInteger(0, 1000)

    class Meta:
        model = models.BankAccount

class OperationFactory(DjangoModelFactory):
    amount = fuzzy.FuzzyInteger(0, 1000)
    sender = SubFactory(BankAccountFactory)
    receiver = SubFactory(BankAccountFactory)
    
    class Meta:
        model = models.Operation

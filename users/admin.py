from django.contrib import admin

# Register your models here.
from users.models import BankAccount, Operation


class AdminBankAccount(admin.ModelAdmin):
    list_display = ('id', 'user', 'balance')


admin.site.register(BankAccount, AdminBankAccount)


class AdminOperation(admin.ModelAdmin):
    list_display = ('amount', 'message', 'sender', 'receiver', 'message')


admin.site.register(Operation, AdminOperation)

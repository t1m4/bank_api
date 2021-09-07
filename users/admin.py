from django.contrib import admin

# Register your models here.
from users.models import BankAccount

admin.site.register(BankAccount)
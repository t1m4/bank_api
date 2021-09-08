from django.urls import path, include
from rest_framework import routers

from users import views

router = routers.DefaultRouter()
router.register(r'accounts', views.CreateBankAccount, basename='accounts')

urlpatterns = [
    path('transfer/', views.TransferView.as_view(), name='users-transfer'),
    path('', include(router.urls)),
]

from django.urls import path

from users import views

# router = routers.DefaultRouter()
# router.register(r'users', views.CreateBankAccount, basename='users')

urlpatterns = [
    path('create_card/', views.CreateBankAccount.as_view(), name='users-create'),
    path('transfer/', views.TransferView.as_view(), name='users-transfer')
    # path('', include(router.urls)),
]

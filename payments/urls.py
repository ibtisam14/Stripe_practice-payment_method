from django.urls import path
from .views import CreateCheckoutSessionView, ManualTransferView

urlpatterns = [
    path('checkout/', CreateCheckoutSessionView.as_view()),
    path('manual-transfer/', ManualTransferView.as_view()), 
]

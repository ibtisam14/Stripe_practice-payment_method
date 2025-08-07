from django.urls import path
from .views import (
    CreateAndConfirmPaymentIntentView,
    CreateCheckoutSessionView,           # ✅ NEW
    ManualTransferView,
    GetCheckoutSessionTotalView
)

urlpatterns = [
    path('checkout/', CreateAndConfirmPaymentIntentView.as_view()),  # immediate backend charge (no cart)
    path('create-checkout-session/', CreateCheckoutSessionView.as_view()),  # ✅ Stripe Checkout with cart
    path('manual-transfer/', ManualTransferView.as_view()),
    path('session/', GetCheckoutSessionTotalView.as_view())
]

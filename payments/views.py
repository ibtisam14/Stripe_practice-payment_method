import stripe
import os
import json
from django.http import JsonResponse, HttpResponse
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator

# Load Stripe keys from environment variables
stripe.api_key = os.getenv('STRIPE_SECRET_KEY')
STRIPE_SUCCESS_URL = os.getenv('STRIPE_SUCCESS_URL')
STRIPE_CANCEL_URL = os.getenv('STRIPE_CANCEL_URL')

connected_account_id = "acct_1Rt2JIKTcDr8jXDm"  # Replace with real ID


def create_connected_account():
    account = stripe.Account.create(
        type="express",
        country="US",
        email="vendor@example.com",
    )
    return account.id
@method_decorator(csrf_exempt, name='dispatch')
class CreateCheckoutSessionView(View):
    def post(self, request, *args, **kwargs):
        try:
            data = json.loads(request.body)
            price_in_dollars = data.get("price")

            if not price_in_dollars:
                return JsonResponse({"error": "Price (in dollars) is required."}, status=400)

            try:
                price_in_dollars = float(price_in_dollars)
                price_in_cents = int(price_in_dollars * 100)
            except ValueError:
                return JsonResponse({"error": "Invalid price format."}, status=400)

            checkout_session = stripe.checkout.Session.create(
                payment_method_types=['card'],
                line_items=[{
                    'price_data': {
                        'currency': 'usd',
                        'product_data': {
                            'name': "Custom Product",
                        },
                        'unit_amount': price_in_cents,
                    },
                    'quantity': 1,
                }],
                mode='payment',
                success_url=STRIPE_SUCCESS_URL,
                cancel_url=STRIPE_CANCEL_URL,
            )

            return JsonResponse({
                'checkout_url': checkout_session.url,
                'price_in_dollars': f"${price_in_dollars:.2f}",
                'price_in_cents': price_in_cents  
            })

        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

@method_decorator(csrf_exempt, name='dispatch')
class ManualTransferView(View):
    def post(self, request, *args, **kwargs):
        try:
            data = json.loads(request.body)
            amount_dollars = data.get("amount")

            if not amount_dollars:
                return JsonResponse({"error": "Amount is required."}, status=400)

            amount_cents = int(float(amount_dollars) * 100)

            transfer = stripe.Transfer.create(
                amount=amount_cents,
                currency='usd',
                destination=connected_account_id,
                description='Manual test transfer',
            )

            return JsonResponse({
                "message": "Transfer successful",
                "transfer_id": transfer.id
            })

        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

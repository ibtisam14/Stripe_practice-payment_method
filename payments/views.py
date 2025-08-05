import stripe
import os
import json
from django.http import JsonResponse
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator

# Load Stripe keys from environment variables
stripe.api_key = os.getenv('STRIPE_SECRET_KEY')
STRIPE_PUBLISHABLE_KEY = os.getenv('STRIPE_PUBLISHABLE_KEY')
STRIPE_SUCCESS_URL = os.getenv('STRIPE_SUCCESS_URL')
STRIPE_CANCEL_URL = os.getenv('STRIPE_CANCEL_URL')


@method_decorator(csrf_exempt, name='dispatch')
class CreateCheckoutSessionView(View):
    def post(self, request, *args, **kwargs):
        try:
            data = json.loads(request.body)
            price_in_dollars = data.get("price")  # user sends price in dollars

            if not price_in_dollars:
                return JsonResponse({"error": "Price (in dollars) is required."}, status=400)

            try:
                # Convert dollars to cents for Stripe
                price_in_dollars = float(price_in_dollars)
                price_in_cents = int(price_in_dollars * 100)
            except ValueError:
                return JsonResponse({"error": "Invalid price format."}, status=400)

            # Create Stripe Checkout Session
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
                'price_in_dollars': f"${price_in_dollars:.2f}"
            })

        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

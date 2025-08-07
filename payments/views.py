import stripe
import os
import json
from django.http import JsonResponse
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator

# Load Stripe keys from environment variables
stripe.api_key = os.getenv('STRIPE_SECRET_KEY')
STRIPE_SUCCESS_URL = os.getenv('STRIPE_SUCCESS_URL', 'https://example.com/success')
STRIPE_CANCEL_URL = os.getenv('STRIPE_CANCEL_URL', 'https://example.com/cancel')

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
            products = data.get("products")

            if not products or not isinstance(products, list):
                return JsonResponse({"error": "'products' must be a list of product objects."}, status=400)

            line_items = []
            total_cents = 0
            items_count = 0

            for product in products:
                try:
                    name = product.get("name")
                    price = float(product.get("price"))
                    quantity = int(product.get("quantity"))

                    if not name or price <= 0 or quantity <= 0:
                        return JsonResponse({"error": f"Invalid product entry: {product}"}, status=400)

                    unit_price_cents = int(price * 100)
                    total_cents += unit_price_cents * quantity
                    items_count += quantity

                    line_items.append({
                        'price_data': {
                            'currency': 'usd',
                            'product_data': {
                                'name': name,
                            },
                            'unit_amount': unit_price_cents,
                        },
                        'quantity': quantity,
                    })

                except (ValueError, TypeError):
                    return JsonResponse({"error": f"Invalid product data: {product}"}, status=400)

            checkout_session = stripe.checkout.Session.create(
                payment_method_types=['card'],
                line_items=line_items,
                mode='payment',
                success_url=STRIPE_SUCCESS_URL + '?session_id={CHECKOUT_SESSION_ID}',
                cancel_url=STRIPE_CANCEL_URL,
                metadata={'total_items': str(items_count)}
            )

            return JsonResponse({
                "checkout_session_id": checkout_session.id,
                "checkout_url": checkout_session.url,
                "total_price_in_dollars": f"${total_cents / 100:.2f}",
                "total_price_in_cents": total_cents,
                "items_count": items_count,
                "message": "Redirect user to checkout_url to complete payment"
            })

        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

@method_decorator(csrf_exempt, name='dispatch')
class CreateAndConfirmPaymentIntentView(View):
    def post(self, request, *args, **kwargs):
        try:
            data = json.loads(request.body)
            products = data.get("products")

            if not products or not isinstance(products, list):
                return JsonResponse({"error": "'products' must be a list of product objects."}, status=400)

            total_cents = 0
            items_count = 0

            for product in products:
                try:
                    price = float(product.get("price"))
                    quantity = int(product.get("quantity"))

                    if price <= 0 or quantity <= 0:
                        return JsonResponse({"error": f"Invalid product entry: {product}"}, status=400)

                    unit_price_cents = int(price * 100)
                    total_cents += unit_price_cents * quantity
                    items_count += quantity
                except (ValueError, TypeError):
                    return JsonResponse({"error": f"Invalid product data: {product}"}, status=400)

            intent = stripe.PaymentIntent.create(
                amount=total_cents,
                currency="usd",
                payment_method="pm_card_visa",
                confirm=True,
                automatic_payment_methods={
                    "enabled": True,
                    "allow_redirects": "never"
                }
            )

            return JsonResponse({
                "payment_intent_id": intent.id,
                "status": intent.status,
                "total_price_in_dollars": f"${total_cents / 100:.2f}",
                "total_price_in_cents": total_cents,
                "items_count": items_count
            })

        except stripe.error.CardError as e:
            return JsonResponse({"error": f"Card declined: {e.user_message}"}, status=400)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

@method_decorator(csrf_exempt, name='dispatch')
class GetCheckoutSessionDetailsView(View):
    """Get details of a completed checkout session"""
    def post(self, request, *args, **kwargs):
        try:
            data = json.loads(request.body)
            session_id = data.get("session_id")

            if not session_id:
                return JsonResponse({"error": "Checkout session ID is required."}, status=400)

            session = stripe.checkout.Session.retrieve(
                session_id,
                expand=['line_items']
            )

            total_cents = session.get("amount_total")
            currency = session.get("currency")
            payment_status = session.get("payment_status")

            item_list = []
            if session.line_items and session.line_items.data:
                for item in session.line_items.data:
                    item_info = {
                        "product_name": item.description or "Product",
                        "unit_price_in_cents": item.price.unit_amount if item.price else 0,
                        "unit_price_in_dollars": f"${(item.price.unit_amount or 0) / 100:.2f}",
                        "quantity": item.quantity,
                        "total_price_in_cents": item.amount_total,
                        "total_price_in_dollars": f"${item.amount_total / 100:.2f}"
                    }
                    item_list.append(item_info)

            return JsonResponse({
                "session_id": session_id,
                "payment_status": payment_status,
                "total_price_in_cents": total_cents,
                "total_price_in_dollars": f"${total_cents / 100:.2f}" if total_cents else "$0.00",
                "currency": currency,
                "items": item_list,
                "customer_email": session.customer_details.email if session.customer_details else None
            })

        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)


@method_decorator(csrf_exempt, name='dispatch')
class ManualTransferView(View):
    """Transfer funds to connected account"""
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
                "transfer_id": transfer.id,
                "amount_transferred": f"${amount_dollars}"
            })

        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)


# Legacy method kept for backward compatibility
@method_decorator(csrf_exempt, name='dispatch')
class GetCheckoutSessionTotalView(View):
    def post(self, request, *args, **kwargs):
        # Redirect to the new method
        view = GetCheckoutSessionDetailsView()
        return view.post(request, *args, **kwargs)
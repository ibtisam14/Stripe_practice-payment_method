# Stripe Checkout Integration with Django

A simple Django application integrating [Stripe Checkout](https://stripe.com/docs/checkout/quickstart) for accepting online payments.

## 💡 Features

- Django-based backend
- Stripe Checkout Session integration
- Success and cancel pages
- Stripe webhook for handling payment events
- Environment variable support via `.env`
- Basic HTML template for testing checkout button

---

## 🛠 Requirements

- Python 3.11+
- Django 4.x
- Stripe Python SDK

---

## 📁 Project Structure

stripe_checkout_project/
│
├── config/ # Django project config
│ └── urls.py # Includes app URLs
│
├── payments/ # Core app with Stripe logic
│ ├── templates/ # HTML files
│ │ ├── checkout.html
│ │ ├── success.html
│ │ └── cancel.html
│ ├── views.py # All Stripe-related views
│ ├── urls.py # App-level routing
│ └── ...
│
├── .env # Secrets file (not tracked in git)
├── requirements.txt
└── manage.py

yaml
Copy
Edit

---

## 🚀 Installation

1. **Clone the repository**
```bash
git clone https://github.com/your-username/stripe-checkout-django.git
cd stripe-checkout-django
Create and activate virtual environment

bash
Copy
Edit
python -m venv .venv
.venv\Scripts\activate  # On Windows
Install dependencies

bash
Copy
Edit
pip install -r requirements.txt
Create .env file in the root directory

dotenv
Copy
Edit
STRIPE_SECRET_KEY=your_stripe_secret_key
STRIPE_PUBLISHABLE_KEY=your_stripe_publishable_key
STRIPE_WEBHOOK_SECRET=your_webhook_secret
STRIPE_SUCCESS_URL=http://127.0.0.1:8000/success/
STRIPE_CANCEL_URL=http://127.0.0.1:8000/cancel/
🔧 Run the Project
bash
Copy
Edit
python manage.py runserver
Visit:

Checkout Page: http://127.0.0.1:8000/checkout/

Create Checkout Session API: POST → http://127.0.0.1:8000/pay/

Success: http://127.0.0.1:8000/success/

Cancel: http://127.0.0.1:8000/cancel/

Webhook (Stripe backend): POST → /webhook/

🔄 Endpoints
Route	Method	Description
/checkout/	GET	Shows Stripe Checkout Button
/pay/	POST	Creates a new Checkout Session
/success/	GET	Shown after successful payment
/cancel/	GET	Shown if payment is canceled
/webhook/	POST	Stripe webhook handler
# models.py
from django.db import models

class Product(models.Model):
    name = models.CharField(max_length=100)
    price = models.IntegerField(help_text="Price in cents (e.g. 2000 = $20.00)")

    def __str__(self):
        return self.name

class Order(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    stripe_session_id = models.CharField(max_length=255)
    is_paid = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

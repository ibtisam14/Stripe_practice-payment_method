# payments/migrations/0002_insert_sample_products.py

from django.db import migrations

def insert_sample_products(apps, schema_editor):
    Product = apps.get_model('payments', 'Product')
    products = [
        ('Basic T-Shirt', 1500),
        ('Premium Hoodie', 4500),
        ('Sneakers', 7000),
        ('Socks Pack', 500),
        ('Denim Jeans', 3500),
        ('Cap', 1200),
        ('Sports Shorts', 2200),
        ('Jacket', 6000),
        ('Backpack', 3000),
        ('Wrist Watch', 8000),
    ]
    for name, price in products:
        Product.objects.create(name=name, price=price)

class Migration(migrations.Migration):

    dependencies = [
        ('payments', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(insert_sample_products),
    ]

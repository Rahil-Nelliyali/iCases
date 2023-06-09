# Generated by Django 4.2 on 2023-04-20 08:03

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('shop', '0007_remove_wishlistitem_product_remove_wishlistitem_user_and_more'),
        ('carts', '0002_remove_cartitem_variations_cartitem_variations'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='cartitem',
            name='variations',
        ),
        migrations.AddField(
            model_name='cartitem',
            name='variations',
            field=models.ManyToManyField(blank=True, to='shop.variation'),
        ),
    ]

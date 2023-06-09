# Generated by Django 4.2 on 2023-04-18 12:20

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('shop', '0005_productreview_review_text_wishlist'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='wishlist',
            name='product',
        ),
        migrations.RemoveField(
            model_name='wishlist',
            name='user',
        ),
        migrations.AddField(
            model_name='wishlist',
            name='wishlist_id',
            field=models.CharField(blank=True, max_length=150),
        ),
        migrations.CreateModel(
            name='WishlistItem',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('product', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='shop.product')),
                ('user', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
                ('wishlist', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='shop.wishlist')),
            ],
        ),
    ]

# Generated by Django 5.1.7 on 2025-04-11 16:37

import uuid
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('application', '0006_event_member_discount_price_event_standard_price'),
    ]

    operations = [
        migrations.AlterField(
            model_name='virtualpayment',
            name='transaction_id',
            field=models.UUIDField(default=uuid.uuid4, editable=False, unique=True),
        ),
    ]

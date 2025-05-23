# Generated by Django 5.1.7 on 2025-04-11 17:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('application', '0007_alter_virtualpayment_transaction_id'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='event',
            name='registration_fee',
        ),
        migrations.AlterField(
            model_name='virtualpayment',
            name='payment_method',
            field=models.CharField(choices=[('card', 'Credit/Debit Card'), ('upi', 'UPI'), ('netbanking', 'Net Banking')], max_length=20),
        ),
    ]
